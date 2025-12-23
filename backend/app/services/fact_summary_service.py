"""
Fact Summary Service - Business logic for case fact summary generation
014-case-fact-summary: T004, T008-T010, T017, T028

Orchestrates:
- Evidence collection from DynamoDB
- Consultation collection from PostgreSQL (상담 내역)
- GPT-4o-mini for summary generation
- Fact summary storage in DynamoDB
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional

from sqlalchemy.orm import Session

from app.repositories.case_repository import CaseRepository
from app.repositories.case_member_repository import CaseMemberRepository
from app.repositories.consultation_repository import ConsultationRepository
from app.utils.dynamo import (
    get_evidence_by_case,
    get_case_fact_summary,
    put_case_fact_summary,
    update_case_fact_summary,
    backup_and_regenerate_fact_summary,
)
from app.utils.openai_client import generate_chat_completion
from app.middleware import NotFoundError, PermissionError, ValidationError
from app.schemas.fact_summary import (
    FactSummaryResponse,
    FactSummaryGenerateResponse,
    FactSummaryUpdateResponse,
)

logger = logging.getLogger(__name__)


class FactSummaryService:
    """
    Service for case fact summary generation and management.

    Workflow:
    1. Collect evidence summaries from DynamoDB
    2. Generate integrated fact summary using GPT-4o-mini
    3. Store in DynamoDB (leh_case_summary table)
    4. Allow lawyer to edit and save modifications
    """

    def __init__(self, db: Session):
        self.db = db
        self.case_repo = CaseRepository(db)
        self.member_repo = CaseMemberRepository(db)
        self.consultation_repo = ConsultationRepository(db)

    def get_fact_summary(self, case_id: str, user_id: str) -> Optional[FactSummaryResponse]:
        """
        Get stored fact summary for a case (T012 endpoint logic)

        Args:
            case_id: Case ID
            user_id: Current user ID for permission check

        Returns:
            FactSummaryResponse or None if not found
        """
        # Permission check
        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("사건 접근 권한이 없습니다")

        # Get from DynamoDB
        summary_data = get_case_fact_summary(case_id)
        if not summary_data:
            return None

        return FactSummaryResponse(
            case_id=summary_data.get("case_id"),
            ai_summary=summary_data.get("ai_summary", ""),
            modified_summary=summary_data.get("modified_summary"),
            evidence_ids=summary_data.get("evidence_ids", []),
            fault_types=summary_data.get("fault_types", []),
            created_at=datetime.fromisoformat(summary_data["created_at"].replace("Z", "+00:00")),
            modified_at=datetime.fromisoformat(summary_data["modified_at"].replace("Z", "+00:00")) if summary_data.get("modified_at") else None,
            modified_by=summary_data.get("modified_by"),
            has_previous_version=bool(summary_data.get("previous_version")),
        )

    def generate_fact_summary(
        self,
        case_id: str,
        user_id: str,
        force_regenerate: bool = False
    ) -> FactSummaryGenerateResponse:
        """
        Generate AI fact summary from evidence (T010, T011 endpoint logic)

        Args:
            case_id: Case ID
            user_id: Current user ID
            force_regenerate: If True, regenerate even if summary exists

        Returns:
            FactSummaryGenerateResponse with generated summary
        """
        logger.info(f"[FactSummary] Generating for case_id={case_id}, force={force_regenerate}")

        # Permission check
        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("사건 접근 권한이 없습니다")

        # Check case exists
        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

        # Check if summary already exists
        existing = get_case_fact_summary(case_id)
        if existing and not force_regenerate:
            raise ValidationError("사실관계가 이미 존재합니다. 재생성하려면 force_regenerate=true를 사용하세요.")

        # Collect evidence summaries
        evidence_list = self._collect_evidence_summaries(case_id)

        # Collect consultation records (상담 내역)
        consultation_list = self._collect_consultations(case_id)

        # 증거나 상담 내역 중 하나는 있어야 함
        if not evidence_list and not consultation_list:
            raise ValidationError("분석된 증거 또는 상담 내역이 없습니다. 증거를 업로드하거나 상담 내역을 입력한 후 다시 시도하세요.")

        # Extract fault types from evidence
        fault_types = self._extract_fault_types(evidence_list)

        # Build prompt and generate summary (상담 내역 포함)
        prompt_messages = self._build_generation_prompt(evidence_list, case.title, consultation_list)
        ai_summary = generate_chat_completion(
            messages=prompt_messages,
            temperature=0.3,
            max_tokens=4000
        )

        # Prepare summary data
        evidence_ids = [e.get("evidence_id") for e in evidence_list if e.get("evidence_id")]
        summary_data = {
            "case_id": case_id,
            "ai_summary": ai_summary,
            "evidence_ids": evidence_ids,
            "fault_types": fault_types,
        }

        # Save to DynamoDB
        if existing and force_regenerate:
            # Backup previous version and save new
            put_case_fact_summary(backup_and_regenerate_fact_summary(case_id, summary_data))
            logger.info(f"[FactSummary] Regenerated with backup for case_id={case_id}")
        else:
            # First time generation
            put_case_fact_summary(summary_data)
            logger.info(f"[FactSummary] Created new summary for case_id={case_id}")

        # 017-party-graph-improvement: Auto-extract parties from fact summary
        # DISABLED: Gemini가 형태소를 인물로 오인식하는 문제로 일시 비활성화
        # 프롬프트 개선 후 재활성화 예정
        # self._auto_extract_parties(case_id, user_id, ai_summary)

        return FactSummaryGenerateResponse(
            case_id=case_id,
            ai_summary=ai_summary,
            evidence_count=len(evidence_list),
            fault_types=fault_types,
            generated_at=datetime.now(timezone.utc),
        )

    def update_fact_summary(
        self,
        case_id: str,
        user_id: str,
        modified_summary: str
    ) -> FactSummaryUpdateResponse:
        """
        Update fact summary with lawyer's modifications (T017, T018 endpoint logic)

        Args:
            case_id: Case ID
            user_id: Current user ID
            modified_summary: Lawyer-edited summary text

        Returns:
            FactSummaryUpdateResponse
        """
        logger.info(f"[FactSummary] Updating for case_id={case_id} by user_id={user_id}")

        # Permission check
        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("사건 접근 권한이 없습니다")

        # Check if summary exists
        existing = get_case_fact_summary(case_id)
        if not existing:
            raise NotFoundError("FactSummary")

        # Update in DynamoDB
        success = update_case_fact_summary(case_id, modified_summary, user_id)
        if not success:
            raise ValidationError("사실관계 수정에 실패했습니다")

        modified_at = datetime.now(timezone.utc)
        logger.info(f"[FactSummary] Updated successfully for case_id={case_id}")

        return FactSummaryUpdateResponse(
            case_id=case_id,
            modified_summary=modified_summary,
            modified_at=modified_at,
            modified_by=user_id,
        )

    def _collect_evidence_summaries(self, case_id: str) -> List[Dict]:
        """
        Collect evidence with AI summaries from DynamoDB (T009)

        Args:
            case_id: Case ID

        Returns:
            List of evidence with ai_summary, sorted by timestamp
        """
        evidence_list = get_evidence_by_case(case_id)

        # Filter to only completed evidence with summaries
        filtered = [
            e for e in evidence_list
            if e.get("status") == "completed" and e.get("ai_summary")
        ]

        # Sort by timestamp (oldest first for chronological story)
        filtered.sort(key=lambda x: x.get("timestamp") or x.get("created_at") or "", reverse=False)

        logger.info(f"[FactSummary] Collected {len(filtered)} evidence summaries for case_id={case_id}")
        return filtered

    def _collect_consultations(self, case_id: str) -> List[Dict]:
        """
        Collect consultation records from PostgreSQL

        Args:
            case_id: Case ID

        Returns:
            List of consultation dicts, sorted by date (oldest first)
        """
        consultations = self.consultation_repo.get_by_case_id(case_id, limit=100)

        consultation_list = []
        for c in consultations:
            consultation_list.append({
                "id": c.id,
                "date": c.date.isoformat() if c.date else "",
                "summary": c.summary or "",
            })

        # Sort by date (oldest first for chronological story)
        consultation_list.sort(key=lambda x: x.get("date") or "", reverse=False)

        logger.info(f"[FactSummary] Collected {len(consultation_list)} consultations for case_id={case_id}")
        return consultation_list

    def _extract_fault_types(self, evidence_list: List[Dict]) -> List[str]:
        """
        Extract unique fault types from evidence article_840_tags

        Args:
            evidence_list: List of evidence metadata

        Returns:
            List of unique fault type labels
        """
        fault_types = set()

        for evidence in evidence_list:
            tags = evidence.get("article_840_tags")
            if tags and isinstance(tags, dict):
                categories = tags.get("categories", [])
                for cat in categories:
                    if isinstance(cat, str) and cat not in ["general", "일반"]:
                        fault_types.add(cat)

            labels = evidence.get("labels")
            if labels and isinstance(labels, list):
                for label in labels:
                    if isinstance(label, str) and label not in ["general", "일반"]:
                        fault_types.add(label)

        return list(fault_types)

    def _build_generation_prompt(
        self,
        evidence_list: List[Dict],
        case_title: str = "",
        consultation_list: Optional[List[Dict]] = None
    ) -> List[Dict[str, str]]:
        """
        Build GPT prompt for fact summary generation (T008)

        Args:
            evidence_list: List of evidence with ai_summary
            case_title: Optional case title for context
            consultation_list: Optional list of consultation records

        Returns:
            List of message dicts for OpenAI API
        """
        # Format evidence summaries
        evidence_text = ""
        for i, evidence in enumerate(evidence_list, 1):
            timestamp = evidence.get("timestamp") or evidence.get("created_at") or "날짜 미상"
            summary = evidence.get("ai_summary", "")
            evidence_type = evidence.get("type", "")
            labels = evidence.get("labels", [])
            labels_str = ", ".join(labels) if labels else ""

            # 015-evidence-speaker-mapping: Include speaker mapping info
            speaker_info = ""
            speaker_mapping = evidence.get("speaker_mapping")
            if speaker_mapping and isinstance(speaker_mapping, dict):
                # Format: 나=김동우, 상대방=김도연
                mapping_parts = []
                for label, item in speaker_mapping.items():
                    if isinstance(item, dict):
                        party_name = item.get("party_name", "")
                        if party_name:
                            mapping_parts.append(f"{label}={party_name}")
                if mapping_parts:
                    speaker_info = f"[화자 정보: {', '.join(mapping_parts)}]"

            evidence_text += f"""
[증거{i}] ({evidence_type}) {timestamp}
{speaker_info}
{summary}
{f"관련 태그: {labels_str}" if labels_str else ""}
---
"""

        # Format consultation records (상담 내역) - 날짜와 내용만 포함
        consultation_text = ""
        if consultation_list:
            for i, consultation in enumerate(consultation_list, 1):
                date = consultation.get("date", "날짜 미상")
                summary = consultation.get("summary", "")

                consultation_text += f"""
[상담{i}] {date}
{summary}
---
"""

        system_prompt = """당신은 이혼 소송 전문 법률 보조 AI입니다.
아래 증거들과 상담 내역을 종합하여 사건의 사실관계를 시간순으로 정리해주세요.

## 작성 규칙:
1. 시간순으로 정렬 (오래된 것 → 최근)
2. 각 사실 앞에 출처 표시: [증거N] 또는 [상담N]
3. 객관적 사실만 기술, 의견이나 추측 배제
4. 유책사유(부정행위, 가정폭력, 악의의 유기 등) 명확히 표시
5. 핵심 사실 위주로 3000자 이내
6. [화자 정보]가 있는 경우, "나", "상대방" 등의 표현을 실제 인물 이름으로 변환하여 기술
7. 상담 내역은 의뢰인의 진술로서 증거의 맥락을 이해하는 데 활용 (단, 상담 내용만으로는 사실 인정 불가, 증거로 뒷받침 필요)

## 출력 형식:
### 사건 개요
[혼인 기간, 당사자 관계 등 기본 정보 - 증거 및 상담에서 추론]

### 사실관계
1. [증거1/상담1] YYYY년 M월 - 구체적 사실
2. [증거2] YYYY년 M월 - 구체적 사실
...

### 유책사유 요약
- 부정행위: 해당 시 기술
- 가정폭력: 해당 시 기술
- 기타: 해당 시 기술

### 증거 보강 필요 사항 (선택)
- 상담에서 진술된 내용 중 아직 증거로 뒷받침되지 않은 사항"""

        # Build user prompt
        user_prompt = f"""## 사건명: {case_title or "이혼 사건"}
"""
        if evidence_text:
            user_prompt += f"""
## 증거 요약:
{evidence_text}
"""
        if consultation_text:
            user_prompt += f"""
## 상담 내역 (의뢰인 진술):
{consultation_text}
"""
        user_prompt += """
위 증거들과 상담 내역을 종합하여 사건의 전체 사실관계를 정리해주세요."""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def _auto_extract_parties(
        self,
        case_id: str,
        user_id: str,
        fact_summary: str
    ) -> None:
        """
        Automatically extract parties and relationships from fact summary (017-party-graph-improvement)

        This is called after fact summary generation to populate party graph.
        Errors are logged but do not fail the main operation.

        Args:
            case_id: Case ID
            user_id: Current user ID
            fact_summary: Generated fact summary text
        """
        try:
            from app.services.party_extraction_service import PartyExtractionService

            extraction_service = PartyExtractionService(self.db)
            result = extraction_service.extract_from_fact_summary(
                case_id=case_id,
                user_id=user_id,
                fact_summary_text=fact_summary  # Pass directly to avoid re-fetching
            )

            logger.info(
                f"[FactSummary] Auto-extracted parties: "
                f"new={result.new_parties_count}, merged={result.merged_parties_count}, "
                f"relationships={result.new_relationships_count}"
            )

        except ImportError as e:
            logger.warning(f"[FactSummary] Party extraction service not available: {e}")
        except Exception as e:
            # Log but don't fail - party extraction is enhancement, not critical
            logger.warning(f"[FactSummary] Party extraction failed (non-critical): {e}")
