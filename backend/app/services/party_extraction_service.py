"""
Party Extraction Service - Extract parties and relationships from fact summary using Gemini
017-party-graph-improvement: Fact-summary 기반 인물/관계 자동 추출
"""

import json
import logging
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import PartyType, RelationshipType
from app.repositories.party_repository import PartyRepository
from app.repositories.case_member_repository import CaseMemberRepository
from app.utils.dynamo import get_case_fact_summary
from app.utils.gemini_client import generate_chat_completion_gemini
from app.middleware import NotFoundError, PermissionError, ValidationError

logger = logging.getLogger(__name__)


@dataclass
class ExtractedPerson:
    """Extracted person from fact summary"""
    name: str
    role: str  # plaintiff, defendant, child, third_party, family
    side: str  # plaintiff_side, defendant_side, neutral
    description: str


@dataclass
class ExtractedRelationship:
    """Extracted relationship from fact summary"""
    from_name: str
    to_name: str
    type: str  # marriage, affair, parent_child, sibling, in_law, cohabit
    description: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@dataclass
class ExtractionResult:
    """Result of party extraction"""
    persons: List[ExtractedPerson]
    relationships: List[ExtractedRelationship]
    new_parties_count: int
    merged_parties_count: int
    new_relationships_count: int
    party_id_map: Dict[str, str]  # name -> party_id mapping


class PartyExtractionService:
    """
    Service for extracting parties and relationships from fact summary using Gemini.

    Workflow:
    1. Get fact summary from DynamoDB
    2. Call Gemini API with structured JSON output prompt
    3. Parse JSON response to extract persons and relationships
    4. Merge with existing parties (by name)
    5. Save to PostgreSQL
    """

    def __init__(self, db: Session):
        self.db = db
        self.party_repo = PartyRepository(db)
        self.member_repo = CaseMemberRepository(db)

    def extract_from_fact_summary(
        self,
        case_id: str,
        user_id: str,
        fact_summary_text: Optional[str] = None
    ) -> ExtractionResult:
        """
        Extract parties and relationships from fact summary.

        Args:
            case_id: Case ID
            user_id: User ID for permission check
            fact_summary_text: Optional fact summary text (if not provided, fetched from DynamoDB)

        Returns:
            ExtractionResult with extracted and merged data
        """
        logger.info(f"[PartyExtraction] Starting extraction for case_id={case_id}")

        # 1. Permission check
        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("사건 접근 권한이 없습니다")

        # 2. Get fact summary - use provided text or fetch from DynamoDB
        if fact_summary_text:
            fact_summary = fact_summary_text
        else:
            summary_data = get_case_fact_summary(case_id)
            if not summary_data:
                raise NotFoundError("FactSummary")
            # Use modified_summary if available, otherwise ai_summary
            fact_summary = summary_data.get("modified_summary") or summary_data.get("ai_summary", "")

        if not fact_summary or len(fact_summary) < 50:
            raise ValidationError("사실관계 요약이 너무 짧습니다. 최소 50자 이상이어야 합니다.")

        # 3. Call Gemini to extract persons and relationships
        extracted_persons, extracted_relationships = self._extract_with_gemini(fact_summary)

        if not extracted_persons:
            logger.warning(f"[PartyExtraction] No persons extracted for case_id={case_id}")
            return ExtractionResult(
                persons=[],
                relationships=[],
                new_parties_count=0,
                merged_parties_count=0,
                new_relationships_count=0,
                party_id_map={}
            )

        # 4. Merge with existing parties and save
        result = self._merge_and_save(case_id, extracted_persons, extracted_relationships)

        logger.info(
            f"[PartyExtraction] Completed for case_id={case_id}: "
            f"new={result.new_parties_count}, merged={result.merged_parties_count}, "
            f"relationships={result.new_relationships_count}"
        )

        return result

    def _extract_with_gemini(
        self,
        fact_summary: str
    ) -> Tuple[List[ExtractedPerson], List[ExtractedRelationship]]:
        """
        Call Gemini API to extract persons and relationships from fact summary.
        Uses 2-step verification to filter out non-person names.

        Returns:
            Tuple of (persons, relationships)
        """
        prompt_messages = self._build_extraction_prompt(fact_summary)

        try:
            # Step 1: Extract persons and relationships
            response = generate_chat_completion_gemini(
                messages=prompt_messages,
                model=settings.GEMINI_MODEL_CHAT,
                temperature=0.1,  # Low temperature for structured output
                max_tokens=2000
            )

            # Parse JSON response
            persons, relationships = self._parse_extraction_response(response)

            if not persons:
                return persons, relationships

            # Step 2: Verify extracted names are actual person names
            verified_persons = self._verify_person_names(persons)

            # Filter relationships to only include verified persons
            verified_names = {p.name for p in verified_persons}
            verified_relationships = [
                r for r in relationships
                if r.from_name in verified_names and r.to_name in verified_names
            ]

            logger.info(
                f"[PartyExtraction] Verification: {len(persons)} -> {len(verified_persons)} persons, "
                f"{len(relationships)} -> {len(verified_relationships)} relationships"
            )

            return verified_persons, verified_relationships

        except Exception as e:
            logger.error(f"[PartyExtraction] Gemini API error: {e}")
            raise ValidationError(f"인물 추출 중 오류가 발생했습니다: {str(e)}")

    # Non-person words to filter out (fallback list)
    NON_PERSON_WORDS = {
        # Time expressions
        "오전", "오후", "저녁", "새벽", "아침", "밤", "점심",
        # Legal terms
        "이혼", "결혼", "합의", "조정", "소송", "재판", "판결", "위자료",
        # Status expressions
        "정됨", "완료", "진행", "확인", "승인", "거부", "취소",
        # General nouns
        "자녀", "부모", "배우자", "친구", "동료", "직장", "회사",
        # Roles (not names)
        "원고", "피고", "증인", "참고인",
        # Other common misidentifications
        "이혼아", "결혼식", "법원", "변호사", "판사",
    }


    def _verify_person_names(
        self,
        persons: List[ExtractedPerson]
    ) -> List[ExtractedPerson]:
        """
        Step 2: Verify extracted names are actual person names using Gemini.
        Filters out time expressions, legal terms, and other non-person words.
        """
        if not persons:
            return []

        # Pre-filter: Remove obvious non-person words before Gemini verification
        pre_filtered = [
            p for p in persons
            if p.name.strip() not in self.NON_PERSON_WORDS
            and len(p.name.strip()) >= 2  # Names should be at least 2 chars
        ]

        if not pre_filtered:
            logger.info("[PartyExtraction] All names filtered by pre-filter")
            return []

        names = [p.name for p in pre_filtered]
        names_str = ", ".join(names)

        verification_prompt = [
            {
                "role": "system",
                "content": """당신은 텍스트에서 실제 사람 이름만 식별하는 전문가입니다.

## 규칙
1. 실제 사람 이름만 선택 (한국 이름, 외국 이름, 별명 포함)
2. 다음은 사람 이름이 아님:
   - 시간 표현: 오전, 오후, 저녁, 새벽, 아침
   - 법률 용어: 이혼, 결혼, 합의, 조정, 소송
   - 상태 표현: 정됨, 완료, 진행, 확인
   - 일반 명사: 자녀, 부모, 배우자, 친구
3. "원고", "피고"는 역할이므로 사람 이름이 아님 (단, "원고 김철수"에서 "김철수"는 이름)

## 출력 형식 (JSON만 출력)
{"valid_names": ["실제 이름1", "실제 이름2"]}"""
            },
            {
                "role": "user",
                "content": f"다음 중 실제 사람 이름만 선택하세요: [{names_str}]"
            }
        ]

        try:
            response = generate_chat_completion_gemini(
                messages=verification_prompt,
                model=settings.GEMINI_MODEL_CHAT,
                temperature=0.0,  # Deterministic for verification
                max_tokens=500
            )

            # Parse response
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            data = json.loads(cleaned)
            valid_names = set(data.get("valid_names", []))

            # Filter persons to only include verified names
            verified_persons = [p for p in persons if p.name in valid_names]

            logger.info(f"[PartyExtraction] Name verification: {names} -> {list(valid_names)}")
            return verified_persons

        except Exception as e:
            logger.warning(f"[PartyExtraction] Name verification failed, using pre-filtered names: {e}")
            # Fallback: return pre-filtered persons (already filtered by NON_PERSON_WORDS)
            return pre_filtered

    def _build_extraction_prompt(self, fact_summary: str) -> List[Dict[str, str]]:
        """Build Gemini prompt for structured extraction"""

        system_prompt = """당신은 이혼 소송 사실관계에서 등장 인물과 관계를 추출하는 전문가입니다.

## 출력 형식 (JSON만 출력, 다른 텍스트 없이)
{
  "persons": [
    {
      "name": "실명 또는 가명",
      "role": "plaintiff|defendant|child|third_party|family",
      "side": "plaintiff_side|defendant_side|neutral",
      "description": "역할 설명 (예: 원고, 40대 남성, 회사원)"
    }
  ],
  "relationships": [
    {
      "from_name": "인물A 이름",
      "to_name": "인물B 이름",
      "type": "marriage|affair|parent_child|sibling|in_law|cohabit",
      "description": "관계 설명",
      "start_date": "YYYY-MM (추정 가능 시, 없으면 null)",
      "end_date": "YYYY-MM (추정 가능 시, 진행중이면 null)"
    }
  ]
}

## 규칙
1. 확실한 정보만 추출 (추측 금지)
2. "원고", "피고" 표현이 있으면 role 필드로 변환
3. 관계는 명확한 증거가 있을 때만 추출
4. 중복 인물 없이 추출
5. 이름이 없는 인물은 역할로 표시 (예: "원고 자녀", "피고 어머니")
6. JSON 외의 텍스트는 출력하지 마세요
7. 다음은 인물이 아니므로 절대 추출하지 마세요:
   - 시간 표현: 오전, 오후, 저녁, 새벽, 아침
   - 법률 용어: 이혼, 결혼, 합의, 조정, 소송, 위자료
   - 상태 표현: 정됨, 완료, 진행, 확인
   - 일반 명사: 자녀, 부모, 배우자, 친구, 동료
   - 역할명: 원고, 피고, 증인, 판사, 변호사"""

        user_prompt = f"""다음 사실관계 요약에서 등장 인물과 관계를 추출해주세요.

## 사실관계 요약
{fact_summary}

위 내용에서 인물과 관계를 JSON 형식으로 추출해주세요."""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

    def _parse_extraction_response(
        self,
        response: str
    ) -> Tuple[List[ExtractedPerson], List[ExtractedRelationship]]:
        """Parse Gemini JSON response"""

        # Clean response - remove markdown code blocks if present
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"[PartyExtraction] JSON parse error: {e}, response: {response[:500]}")
            raise ValidationError("AI 응답을 파싱할 수 없습니다. 다시 시도해주세요.")

        persons = []
        for p in data.get("persons", []):
            if not p.get("name"):
                continue
            persons.append(ExtractedPerson(
                name=p.get("name", "").strip(),
                role=self._normalize_role(p.get("role", "third_party")),
                side=p.get("side", "neutral"),
                description=p.get("description", "")
            ))

        relationships = []
        for r in data.get("relationships", []):
            if not r.get("from_name") or not r.get("to_name"):
                continue
            relationships.append(ExtractedRelationship(
                from_name=r.get("from_name", "").strip(),
                to_name=r.get("to_name", "").strip(),
                type=self._normalize_relationship_type(r.get("type", "other")),
                description=r.get("description", ""),
                start_date=r.get("start_date"),
                end_date=r.get("end_date")
            ))

        return persons, relationships

    def _normalize_role(self, role: str) -> str:
        """Normalize role string to PartyType enum value"""
        role_map = {
            "plaintiff": "plaintiff",
            "원고": "plaintiff",
            "defendant": "defendant",
            "피고": "defendant",
            "child": "child",
            "자녀": "child",
            "third_party": "third_party",
            "제3자": "third_party",
            "family": "family",
            "친족": "family",
            "witness": "third_party",
            "증인": "third_party",
        }
        return role_map.get(role.lower(), "third_party")

    def _normalize_relationship_type(self, rel_type: str) -> str:
        """Normalize relationship type string"""
        type_map = {
            "marriage": "marriage",
            "혼인": "marriage",
            "부부": "marriage",
            "affair": "affair",
            "불륜": "affair",
            "외도": "affair",
            "parent_child": "parent_child",
            "부모자녀": "parent_child",
            "sibling": "sibling",
            "형제자매": "sibling",
            "in_law": "in_law",
            "인척": "in_law",
            "시댁": "in_law",
            "처가": "in_law",
            "cohabit": "cohabit",
            "동거": "cohabit",
        }
        return type_map.get(rel_type.lower(), "marriage")

    def _merge_and_save(
        self,
        case_id: str,
        persons: List[ExtractedPerson],
        relationships: List[ExtractedRelationship]
    ) -> ExtractionResult:
        """
        Merge extracted data with existing parties and save to database.
        Uses name-based matching for merging.
        """
        # Get existing parties for this case
        existing_parties = self.party_repo.get_parties_by_case(case_id)
        existing_by_name = {p.name.lower(): p for p in existing_parties}

        party_id_map: Dict[str, str] = {}  # name -> party_id
        new_count = 0
        merged_count = 0

        # Default position for new nodes (will be arranged by frontend)
        base_x = 100
        base_y = 100

        # Process persons
        for i, person in enumerate(persons):
            name_lower = person.name.lower()

            if name_lower in existing_by_name:
                # Merge: Update existing party with new info if missing
                existing = existing_by_name[name_lower]
                party_id_map[person.name] = existing.id

                # Update fields if they were auto-extracted (don't override manual edits)
                if existing.is_auto_extracted:
                    # Could update description, etc.
                    pass

                merged_count += 1
                logger.debug(f"[PartyExtraction] Merged party: {person.name} -> {existing.id}")
            else:
                # Create new party
                try:
                    party_type = PartyType(person.role)
                except ValueError:
                    party_type = PartyType.THIRD_PARTY

                new_party = self.party_repo.create_party(
                    case_id=case_id,
                    party_type=party_type,
                    name=person.name,
                    alias=None,
                    birth_year=None,
                    occupation=None,
                    position_x=base_x + (i % 4) * 200,
                    position_y=base_y + (i // 4) * 150,
                    is_auto_extracted=True,
                    extraction_confidence=0.85,
                    source_evidence_id=None,  # From fact summary, not specific evidence
                    extra_data={"description": person.description, "side": person.side}
                )

                party_id_map[person.name] = new_party.id
                existing_by_name[name_lower] = new_party
                new_count += 1
                logger.debug(f"[PartyExtraction] Created party: {person.name} -> {new_party.id}")

        # Process relationships
        new_rel_count = 0
        for rel in relationships:
            from_id = party_id_map.get(rel.from_name)
            to_id = party_id_map.get(rel.to_name)

            if not from_id or not to_id:
                logger.warning(
                    f"[PartyExtraction] Skipping relationship: {rel.from_name} -> {rel.to_name} "
                    f"(party not found)"
                )
                continue

            if from_id == to_id:
                continue  # Skip self-references

            # Check if relationship already exists
            existing_rel = self.party_repo.get_relationship_by_parties(
                case_id, from_id, to_id
            )

            if existing_rel:
                logger.debug(f"[PartyExtraction] Relationship already exists: {from_id} -> {to_id}")
                continue

            # Create new relationship
            try:
                rel_type = RelationshipType(rel.type)
            except ValueError:
                rel_type = RelationshipType.MARRIAGE

            self.party_repo.create_relationship(
                case_id=case_id,
                source_party_id=from_id,
                target_party_id=to_id,
                relationship_type=rel_type,
                is_auto_extracted=True,
                extraction_confidence=0.8,
                evidence_text=rel.description,
                notes=None
            )
            new_rel_count += 1
            logger.debug(f"[PartyExtraction] Created relationship: {from_id} -> {to_id} ({rel.type})")

        return ExtractionResult(
            persons=persons,
            relationships=relationships,
            new_parties_count=new_count,
            merged_parties_count=merged_count,
            new_relationships_count=new_rel_count,
            party_id_map=party_id_map
        )
