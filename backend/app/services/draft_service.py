"""
Draft Service - Business logic for draft generation with RAG
Orchestrates Qdrant RAG + OpenAI GPT-4o for draft preview

Refactored in Phase 13: Extracted helper services for better modularity
- RAGOrchestrator: RAG search and context formatting
- PromptBuilder: GPT-4o prompt construction
- CitationExtractor: Citation parsing and extraction
"""

from sqlalchemy.orm import Session
from typing import List, Tuple
from datetime import datetime, timezone
from io import BytesIO

from app.db.schemas import (
    DraftPreviewRequest,
    DraftPreviewResponse,
    DraftCitation,
    PrecedentCitation,  # 012-precedent-integration: T034
    DraftExportFormat,
    DraftCreate,
    DraftUpdate,
    DraftResponse,
    DraftListItem
)
from app.db.models import DraftDocument, DraftStatus, DocumentType
from app.repositories.case_repository import CaseRepository
from app.repositories.case_member_repository import CaseMemberRepository
from app.utils.dynamo import get_evidence_by_case
from app.utils.qdrant import (
    search_evidence_by_semantic,
    search_legal_knowledge,
    get_template_schema_for_prompt,
    get_template_by_type
)
from app.utils.openai_client import generate_chat_completion
from app.services.document_renderer import DocumentRenderer
from app.middleware import NotFoundError, PermissionError, ValidationError
from app.services.precedent_service import PrecedentService  # 012-precedent-integration: T032

# Phase 13 refactored services (available for gradual migration)

# Optional: python-docx for DOCX generation
try:
    from docx import Document
    from docx.shared import Pt, Inches  # noqa: F401
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


class DraftService:
    """
    Service for draft generation with RAG
    """

    def __init__(self, db: Session):
        self.db = db
        self.case_repo = CaseRepository(db)
        self.member_repo = CaseMemberRepository(db)
        self.precedent_service = PrecedentService(db)  # 012-precedent-integration: T032

    def generate_draft_preview(
        self,
        case_id: str,
        request: DraftPreviewRequest,
        user_id: str
    ) -> DraftPreviewResponse:
        """
        Generate draft preview using RAG + GPT-4o

        Process:
        1. Validate case access
        2. Retrieve evidence metadata from DynamoDB
        3. Perform semantic search in Qdrant (RAG)
        4. Build GPT-4o prompt with RAG context
        5. Generate draft text
        6. Extract citations

        Args:
            case_id: Case ID
            request: Draft generation request (sections, language, style)
            user_id: User ID requesting draft

        Returns:
            Draft preview with citations

        Raises:
            PermissionError: User does not have access (also for non-existent cases)
            ValidationError: No evidence in case
        """
        # 1. Validate case access - check permission first to prevent info leakage
        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("You do not have access to this case")

        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

        # 2. Retrieve evidence metadata from DynamoDB
        evidence_list = get_evidence_by_case(case_id)

        # Check if there's any evidence
        if not evidence_list:
            raise ValidationError("사건에 증거가 하나도 없습니다. 증거를 업로드한 후 초안을 생성해 주세요.")

        # Filter for completed evidence only (status="done")
        # Note: Currently filtering for reference, may be used for future enhancements
        _ = [ev for ev in evidence_list if ev.get("status") == "done"]

        # 3. Perform semantic RAG search in Qdrant (evidence + legal)
        rag_results = self._perform_rag_search(case_id, request.sections)
        evidence_results = rag_results.get("evidence", [])
        legal_results = rag_results.get("legal", [])

        # 3.5 Search similar precedents (012-precedent-integration: T032)
        precedent_results = self._search_precedents_for_draft(case_id)

        # 4. Check if template exists for JSON output mode
        template = get_template_by_type("이혼소장")
        use_json_output = template is not None

        # 5. Build GPT-4o prompt with RAG context + precedents (012-precedent-integration: T033)
        prompt_messages = self._build_draft_prompt(
            case=case,
            sections=request.sections,
            evidence_context=evidence_results,
            legal_context=legal_results,
            precedent_context=precedent_results,  # 012-precedent-integration: T033
            language=request.language,
            style=request.style
        )

        # 6. Generate draft using GPT-4o
        raw_response = generate_chat_completion(
            messages=prompt_messages,
            temperature=0.3,  # Low temperature for consistent legal writing
            max_tokens=4000
        )

        # 7. Process response based on output mode
        if use_json_output:
            # JSON 출력 모드: 파싱 후 텍스트로 렌더링
            renderer = DocumentRenderer()
            json_doc = renderer.parse_json_response(raw_response)

            if json_doc:
                # JSON 파싱 성공 -> 포맷팅된 텍스트로 변환
                draft_text = renderer.render_to_text(json_doc)
            else:
                # JSON 파싱 실패 -> 원본 응답 사용 (fallback)
                draft_text = raw_response
        else:
            # 기존 텍스트 출력 모드
            draft_text = raw_response

        # 8. Extract citations from RAG results
        citations = self._extract_citations(evidence_results)

        # 8.5 Extract precedent citations (012-precedent-integration: T034)
        precedent_citations = self._extract_precedent_citations(precedent_results)

        return DraftPreviewResponse(
            case_id=case_id,
            draft_text=draft_text,
            citations=citations,
            precedent_citations=precedent_citations,  # 012-precedent-integration: T034
            generated_at=datetime.now(timezone.utc)
        )

    def _perform_rag_search(self, case_id: str, sections: List[str]) -> dict:
        """
        Perform semantic search in Qdrant for RAG context

        Args:
            case_id: Case ID
            sections: Sections being generated

        Returns:
            Dict with 'evidence' and 'legal' results
        """
        # Build search query based on sections
        if "청구원인" in sections:
            # Search for fault evidence (guilt factors)
            query = "이혼 사유 귀책사유 폭언 불화 부정행위"
            evidence_results = search_evidence_by_semantic(
                case_id=case_id,
                query=query,
                top_k=10
            )
            # Search legal knowledge for divorce grounds
            legal_results = search_legal_knowledge(
                query="재판상 이혼 사유 민법 제840조",
                top_k=5,
                doc_type="statute"
            )
        else:
            # General search for all sections
            query = " ".join(sections)
            evidence_results = search_evidence_by_semantic(
                case_id=case_id,
                query=query,
                top_k=5
            )
            legal_results = search_legal_knowledge(
                query="이혼 " + query,
                top_k=3
            )

        return {
            "evidence": evidence_results,
            "legal": legal_results
        }

    def _search_precedents_for_draft(self, case_id: str) -> List[dict]:
        """
        Search similar precedents for draft generation (012-precedent-integration: T032)

        Args:
            case_id: Case ID

        Returns:
            List of precedent dictionaries
        """
        try:
            result = self.precedent_service.search_similar_precedents(
                case_id=case_id,
                limit=5,  # Top 5 precedents for draft context
                min_score=0.5
            )
            # Convert PrecedentCase objects to dicts for prompt building
            return [
                {
                    "case_ref": p.case_ref,
                    "court": p.court,
                    "decision_date": p.decision_date,
                    "summary": p.summary,
                    "key_factors": p.key_factors,
                    "similarity_score": p.similarity_score,
                    "division_ratio": {
                        "plaintiff": p.division_ratio.plaintiff,
                        "defendant": p.division_ratio.defendant
                    } if p.division_ratio else None
                }
                for p in result.precedents
            ]
        except Exception as e:
            # Log error but don't fail draft generation
            import logging
            logging.getLogger(__name__).warning(f"Precedent search failed for case {case_id}: {e}")
            return []

    def _extract_precedent_citations(self, precedent_results: List[dict]) -> List:
        """
        Convert precedent results to PrecedentCitation objects (012-precedent-integration: T034)

        Args:
            precedent_results: List of precedent dictionaries

        Returns:
            List of PrecedentCitation objects
        """
        from urllib.parse import quote

        citations = []
        for p in precedent_results:
            # Generate source_url using 법령한글주소 format
            case_ref = p.get("case_ref", "")
            decision_date = p.get("decision_date", "")
            source_url = None

            if case_ref and decision_date:
                # Convert ISO date to YYYYMMDD
                date_val = decision_date.replace("-", "")
                params = f"{case_ref},{date_val}"
                encoded_params = quote(params, safe="")
                source_url = f"https://www.law.go.kr/판례/({encoded_params})"

            citations.append(
                PrecedentCitation(
                    case_ref=case_ref,
                    court=p.get("court", ""),
                    decision_date=decision_date,
                    summary=p.get("summary", "")[:300],  # Truncate for citation
                    key_factors=p.get("key_factors", []),
                    similarity_score=p.get("similarity_score", 0.0),
                    source_url=source_url
                )
            )
        return citations

    def _format_precedent_context(self, precedent_results: List[dict]) -> str:
        """
        Format precedent results for GPT-4o prompt (012-precedent-integration: T033)

        Args:
            precedent_results: List of precedent dictionaries

        Returns:
            Formatted precedent context string
        """
        if not precedent_results:
            return "(관련 판례 없음)"

        context_parts = []
        for i, p in enumerate(precedent_results, 1):
            case_ref = p.get("case_ref", "")
            court = p.get("court", "")
            decision_date = p.get("decision_date", "")
            summary = p.get("summary", "")
            key_factors = p.get("key_factors", [])
            similarity = p.get("similarity_score", 0.0)

            # Format division ratio if exists
            division_str = ""
            if p.get("division_ratio"):
                dr = p["division_ratio"]
                division_str = f"\n   - 재산분할: 원고 {dr.get('plaintiff', 50)}% / 피고 {dr.get('defendant', 50)}%"

            # Truncate summary safely
            summary_truncated = summary[:200] + "..." if len(summary) > 200 else summary
            factors_str = ', '.join(key_factors) if key_factors else 'N/A'

            context_parts.append(
                f"【판례 {i}】 {case_ref} ({court}, {decision_date}) [유사도: {similarity:.0%}]\n"
                f"   - 요지: {summary_truncated}\n"
                f"   - 주요 요인: {factors_str}{division_str}"
            )

        return "\n\n".join(context_parts)

    def _build_draft_prompt(
        self,
        case: any,
        sections: List[str],
        evidence_context: List[dict],
        legal_context: List[dict],
        precedent_context: List[dict],  # 012-precedent-integration: T033
        language: str,
        style: str
    ) -> List[dict]:
        """
        Build GPT-4o prompt with evidence, legal, and precedent RAG context

        Args:
            case: Case object
            sections: Sections to generate
            evidence_context: Evidence RAG search results
            legal_context: Legal knowledge RAG search results
            precedent_context: Similar precedent search results (012-precedent-integration)
            language: Language (ko/en)
            style: Writing style

        Returns:
            List of messages for GPT-4o
        """
        # Try to get template schema from Qdrant
        template_schema = get_template_schema_for_prompt("이혼소장")
        use_json_output = template_schema is not None

        # System message - define role and constraints
        if use_json_output:
            # JSON 스키마 기반 출력 모드
            system_message = {
                "role": "system",
                "content": f"""당신은 대한민국 가정법원에 제출하는 정식 소장(訴狀)을 작성하는 전문 법률가입니다.

[핵심 원칙 - 반드시 준수]
1. 모든 사실관계, 날짜, 발언 내용은 오직 제공된 "증거 자료"에서만 추출하세요
2. 증거에 없는 내용을 임의로 생성하거나 추측하지 마세요
3. 확인되지 않은 정보는 "확인 필요" 또는 "[미확인]"으로 표시하세요

[출력 형식 - 중요!]
- 반드시 아래 JSON 스키마에 맞춰 출력하세요
- 유효한 JSON 형식으로만 응답하세요 (추가 설명 없이 JSON만)
- 각 섹션의 format 객체는 문서 형식 정보입니다 (들여쓰기, 정렬, 줄간격 등)

[JSON 스키마]
{template_schema}

[증거 인용 방식]
- grounds 섹션의 각 paragraph에 evidence_refs 배열로 증거 번호 포함
- 예: "evidence_refs": ["갑 제1호증", "갑 제2호증"]
- 날짜, 시간, 발언 내용은 증거에서 그대로 가져올 것

[금액 산정]
- 위자료: 증거에서 확인된 유책행위 정도 기반
- 지연손해금: 연 12% (소송촉진법 제3조)

[법적 근거]
- grounds 섹션의 "이혼 사유" 부분에 legal_basis 객체로 민법 제840조 인용

※ AI 생성 초안이며 변호사 검토 필수
"""
            }
        else:
            # 기존 텍스트 출력 모드 (템플릿 없을 경우 fallback)
            system_message = {
                "role": "system",
                "content": """당신은 대한민국 가정법원에 제출하는 정식 소장(訴狀)을 작성하는 전문 법률가입니다.

[핵심 원칙 - 반드시 준수]
1. 모든 사실관계, 날짜, 발언 내용은 오직 제공된 "증거 자료"에서만 추출하세요
2. 증거에 없는 내용을 임의로 생성하거나 추측하지 마세요
3. 확인되지 않은 정보는 "확인 필요" 또는 "[미확인]"으로 표시하세요

[출력 형식]
- 마크다운, 구분선(===, ---) 사용 금지
- 섹션 간 빈 줄 2개로 구분
- 들여쓰기는 공백 4칸

[소장 구조]
1. 소장 제목
2. 당사자 표시 (원고/피고)
3. 청구취지
4. 청구원인
   - 당사자들의 관계
   - 혼인생활의 경과 (증거 기반)
   - 이혼 사유 (민법 제840조 인용, 증거에서 구체적 사실 인용)
   - 위자료 청구 (근거 명시)
5. 입증방법 (증거 목록)
6. 첨부서류
7. 작성일, 원고 서명, 법원 표시

[증거 인용 방식]
- 각 주장에 [갑 제N호증] 형식으로 증거 번호 명시
- 증거의 원문을 직접 인용: "피고는 '...'라고 발언하였다" [갑 제1호증]
- 날짜, 시간, 발언 내용은 증거에서 그대로 가져올 것

[금액 산정]
- 위자료: 증거에서 확인된 유책행위 정도 기반
- 지연손해금: 연 12% (소송촉진법 제3조)

※ AI 생성 초안이며 변호사 검토 필수
"""
            }

        # Build context strings
        evidence_context_str = self._format_evidence_context(evidence_context)
        legal_context_str = self._format_legal_context(legal_context)
        precedent_context_str = self._format_precedent_context(precedent_context)  # 012-precedent-integration: T033

        # User message - include case info, evidence, legal, and precedent context
        if use_json_output:
            user_message = {
                "role": "user",
                "content": f"""다음 정보를 바탕으로 이혼 소송 소장 초안을 JSON 형식으로 작성해 주세요.

**사건 정보:**
- 사건명: {case.title}
- 사건 설명: {case.description or "N/A"}

**생성할 섹션:**
{", ".join(sections)}

**관련 법률 조문:**
{legal_context_str}

**유사 판례 참고자료:**
{precedent_context_str}

**증거 자료:**
{evidence_context_str}

**요청사항:**
- 언어: {language}
- 스타일: {style}
- 위 법률 조문과 증거를 기반으로 법률적 논리를 구성해 주세요
- 이혼 사유는 반드시 민법 제840조를 인용하여 작성하세요
- 유사 판례를 참고하여 위자료/재산분할 청구 논리를 보강하세요
- 각 주장에 대해 evidence_refs 배열에 증거 번호를 포함해 주세요

위 스키마에 맞는 JSON을 출력하세요. JSON 외의 텍스트는 출력하지 마세요.
"""
            }
        else:
            user_message = {
                "role": "user",
                "content": f"""다음 정보를 바탕으로 이혼 소송 소장 초안을 작성해 주세요.

**사건 정보:**
- 사건명: {case.title}
- 사건 설명: {case.description or "N/A"}

**생성할 섹션:**
{", ".join(sections)}

**관련 법률 조문:**
{legal_context_str}

**유사 판례 참고자료:**
{precedent_context_str}

**증거 자료:**
{evidence_context_str}

**요청사항:**
- 언어: {language}
- 스타일: {style}
- 위 법률 조문과 증거를 기반으로 법률적 논리를 구성해 주세요
- 이혼 사유는 반드시 민법 제840조를 인용하여 작성하세요
- 유사 판례를 참고하여 위자료/재산분할 청구 논리를 보강하세요
- 각 주장에 대해 증거 번호를 명시해 주세요 (예: [갑 제1호증], [갑 제2호증])

소장 초안을 작성해 주세요.
"""
            }

        return [system_message, user_message]

    def _format_legal_context(self, legal_results: List[dict]) -> str:
        """
        Format legal knowledge search results for GPT-4o prompt

        Args:
            legal_results: List of legal documents from RAG search

        Returns:
            Formatted legal context string
        """
        if not legal_results:
            return "(관련 법률 조문 없음)"

        context_parts = []
        for doc in legal_results:
            article_number = doc.get("article_number", "")
            statute_name = doc.get("statute_name", "민법")
            # Qdrant payload uses "document" field, not "text"
            content = doc.get("document", "") or doc.get("text", "")

            if article_number and content:
                context_parts.append(f"""
【{statute_name} {article_number}】
{content}
""")

        return "\n".join(context_parts) if context_parts else "(관련 법률 조문 없음)"

    def _format_evidence_context(self, evidence_results: List[dict]) -> str:
        """
        Format evidence search results for GPT-4o prompt

        Args:
            evidence_results: List of evidence documents from RAG search

        Returns:
            Formatted evidence context string
        """
        if not evidence_results:
            return "(증거 자료 없음 - 기본 템플릿으로 작성)"

        context_parts = []
        for i, doc in enumerate(evidence_results, start=1):
            # AI Worker 필드명과 매핑 (chunk_id, document, legal_categories, sender)
            evidence_id = doc.get("chunk_id") or doc.get("id", f"evidence_{i}")
            content = doc.get("document") or doc.get("content", "")
            labels = doc.get("legal_categories") or doc.get("labels", [])
            speaker = doc.get("sender") or doc.get("speaker", "")
            timestamp = doc.get("timestamp", "")

            # Truncate content if too long
            if len(content) > 500:
                content = content[:500] + "..."

            context_parts.append(f"""
[갑 제{i}호증] (ID: {evidence_id})
- 분류: {", ".join(labels) if labels else "N/A"}
- 화자: {speaker or "N/A"}
- 시점: {timestamp or "N/A"}
- 내용: {content}
""")

        return "\n".join(context_parts)

    def _format_rag_context(self, rag_results: List[dict]) -> str:
        """
        Format RAG search results for GPT-4o prompt

        Args:
            rag_results: List of evidence documents from RAG search

        Returns:
            Formatted context string
        """
        if not rag_results:
            return "(증거 자료 없음 - 기본 템플릿으로 작성)"

        context_parts = []
        for i, doc in enumerate(rag_results, start=1):
            evidence_id = doc.get("id", f"evidence_{i}")
            content = doc.get("content", "")
            labels = doc.get("labels", [])
            speaker = doc.get("speaker", "")
            timestamp = doc.get("timestamp", "")

            # Truncate content if too long
            if len(content) > 500:
                content = content[:500] + "..."

            context_parts.append(f"""
[증거 {i}] (ID: {evidence_id})
- 분류: {", ".join(labels) if labels else "N/A"}
- 화자: {speaker or "N/A"}
- 시점: {timestamp or "N/A"}
- 내용: {content}
""")

        return "\n".join(context_parts)

    def _extract_citations(self, rag_results: List[dict]) -> List[DraftCitation]:
        """
        Extract citations from RAG results

        Args:
            rag_results: List of evidence documents from RAG search

        Returns:
            List of DraftCitation objects
        """
        citations = []

        for doc in rag_results:
            evidence_id = doc.get("evidence_id") or doc.get("id")
            content = doc.get("content", "")
            labels = doc.get("labels", [])

            # Create snippet (first 200 chars)
            snippet = content[:200] + "..." if len(content) > 200 else content

            citations.append(
                DraftCitation(
                    evidence_id=evidence_id,
                    snippet=snippet,
                    labels=labels
                )
            )

        return citations

    def export_draft(
        self,
        case_id: str,
        user_id: str,
        export_format: DraftExportFormat = DraftExportFormat.DOCX
    ) -> Tuple[BytesIO, str, str]:
        """
        Export draft as DOCX or PDF file

        Process:
        1. Validate case access
        2. Generate draft preview using RAG + GPT-4o
        3. Convert to requested format (DOCX or PDF)

        Args:
            case_id: Case ID
            user_id: User ID requesting export
            export_format: Output format (docx or pdf)

        Returns:
            Tuple of (file_bytes, filename, content_type)

        Raises:
            PermissionError: User does not have access (also for non-existent cases)
            ValidationError: Export format not supported or missing dependencies
        """
        # 1. Validate case access - check permission first to prevent info leakage
        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("You do not have access to this case")

        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

        # 2. Generate draft preview
        request = DraftPreviewRequest()  # Use default sections
        draft_response = self.generate_draft_preview(case_id, request, user_id)

        # 3. Convert to requested format
        if export_format == DraftExportFormat.DOCX:
            return self._generate_docx(case, draft_response)
        elif export_format == DraftExportFormat.PDF:
            return self._generate_pdf(case, draft_response)
        else:
            raise ValidationError(f"Unsupported export format: {export_format}")

    def _generate_docx(
        self,
        case,
        draft_response: DraftPreviewResponse
    ) -> Tuple[BytesIO, str, str]:
        """
        Generate DOCX file from draft response

        Args:
            case: Case object
            draft_response: Generated draft preview

        Returns:
            Tuple of (file_bytes, filename, content_type)
        """
        if not DOCX_AVAILABLE:
            raise ValidationError(
                "DOCX export is not available. "
                "Please install python-docx: pip install python-docx"
            )

        # Create document
        doc = Document()

        # Title
        title = doc.add_heading("이혼 소송 준비서면 (초안)", level=0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Case info
        doc.add_paragraph()
        case_info = doc.add_paragraph()
        case_info.add_run(f"사건명: {case.title}").bold = True
        doc.add_paragraph(f"생성일시: {draft_response.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")

        # Draft content
        doc.add_heading("본문", level=1)
        for paragraph_text in draft_response.draft_text.split("\n\n"):
            if paragraph_text.strip():
                doc.add_paragraph(paragraph_text.strip())

        # Citations
        if draft_response.citations:
            doc.add_heading("인용 증거", level=1)
            for i, citation in enumerate(draft_response.citations, 1):
                p = doc.add_paragraph()
                p.add_run(f"[증거 {i}] ").bold = True
                p.add_run(f"(ID: {citation.evidence_id})")
                doc.add_paragraph(f"  - 분류: {', '.join(citation.labels) if citation.labels else 'N/A'}")
                doc.add_paragraph(f"  - 내용: {citation.snippet}")

        # Disclaimer
        doc.add_paragraph()
        disclaimer = doc.add_paragraph()
        disclaimer.add_run(
            "⚠️ 본 문서는 AI가 생성한 초안이며, "
            "변호사의 검토 및 수정이 필수입니다."
        ).italic = True

        # Save to BytesIO
        file_buffer = BytesIO()
        doc.save(file_buffer)
        file_buffer.seek(0)

        # Generate filename
        safe_title = case.title.replace(" ", "_")[:30]
        filename = f"draft_{safe_title}_{draft_response.generated_at.strftime('%Y%m%d')}.docx"
        content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

        return file_buffer, filename, content_type

    def _generate_pdf(
        self,
        case,
        draft_response: DraftPreviewResponse
    ) -> Tuple[BytesIO, str, str]:
        """
        Generate PDF file from draft response with Korean font support

        Features:
        - A4 layout for legal documents
        - Korean font support (Noto Sans KR or system fallback)
        - Legal document template structure
        - Citations section

        Args:
            case: Case object
            draft_response: Generated draft preview

        Returns:
            Tuple of (file_bytes, filename, content_type)
        """
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            )
            from reportlab.lib.units import inch, mm
            from reportlab.lib import colors
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

            # Register Korean font
            korean_font_registered = self._register_korean_font(pdfmetrics, TTFont)
            font_name = "NotoSansKR" if korean_font_registered else "Helvetica"

            file_buffer = BytesIO()

            # A4 with proper margins for legal documents
            doc = SimpleDocTemplate(
                file_buffer,
                pagesize=A4,
                leftMargin=25 * mm,
                rightMargin=25 * mm,
                topMargin=25 * mm,
                bottomMargin=25 * mm
            )

            # Create custom styles with Korean font
            styles = getSampleStyleSheet()

            # Title style
            title_style = ParagraphStyle(
                'KoreanTitle',
                parent=styles['Title'],
                fontName=font_name,
                fontSize=18,
                alignment=TA_CENTER,
                spaceAfter=20
            )

            # Heading style
            heading_style = ParagraphStyle(
                'KoreanHeading',
                parent=styles['Heading2'],
                fontName=font_name,
                fontSize=14,
                spaceBefore=15,
                spaceAfter=10
            )

            # Normal text style
            normal_style = ParagraphStyle(
                'KoreanNormal',
                parent=styles['Normal'],
                fontName=font_name,
                fontSize=11,
                leading=16,
                alignment=TA_JUSTIFY,
                spaceAfter=8
            )

            # Citation style
            citation_style = ParagraphStyle(
                'Citation',
                parent=styles['Normal'],
                fontName=font_name,
                fontSize=10,
                leading=14,
                leftIndent=10,
                spaceAfter=6
            )

            # Disclaimer style
            disclaimer_style = ParagraphStyle(
                'Disclaimer',
                parent=styles['Normal'],
                fontName=font_name,
                fontSize=9,
                textColor=colors.grey,
                alignment=TA_CENTER,
                spaceBefore=20
            )

            story = []

            # === Document Header ===
            story.append(Paragraph("이혼 소송 준비서면", title_style))
            story.append(Paragraph("(초 안)", ParagraphStyle(
                'Subtitle',
                parent=normal_style,
                alignment=TA_CENTER,
                fontSize=12,
                spaceAfter=30
            )))

            # === Case Information Table ===
            case_data = [
                ["사 건 명", case.title],
                ["생성일시", draft_response.generated_at.strftime('%Y년 %m월 %d일 %H:%M')],
            ]
            case_table = Table(case_data, colWidths=[80, 350])
            case_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(case_table)
            story.append(Spacer(1, 0.4 * inch))

            # === Main Content ===
            story.append(Paragraph("본 문", heading_style))

            # Split content by paragraphs and add to story
            for paragraph_text in draft_response.draft_text.split("\n\n"):
                cleaned_text = paragraph_text.strip()
                if cleaned_text:
                    # Escape XML special characters
                    cleaned_text = (
                        cleaned_text
                        .replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                    )
                    story.append(Paragraph(cleaned_text, normal_style))

            # === Citations Section ===
            if draft_response.citations:
                story.append(Spacer(1, 0.3 * inch))
                story.append(Paragraph("인용 증거", heading_style))

                for i, citation in enumerate(draft_response.citations, 1):
                    # Citation header
                    labels_str = ", ".join(citation.labels) if citation.labels else "N/A"
                    citation_header = f"<b>[증거 {i}]</b> (ID: {citation.evidence_id})"
                    story.append(Paragraph(citation_header, citation_style))

                    # Citation details
                    story.append(Paragraph(f"분류: {labels_str}", citation_style))

                    # Citation snippet (escape special characters)
                    snippet = (
                        citation.snippet
                        .replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                    )
                    story.append(Paragraph(f"내용: {snippet}", citation_style))
                    story.append(Spacer(1, 0.1 * inch))

            # === Disclaimer ===
            story.append(Spacer(1, 0.5 * inch))
            story.append(Paragraph(
                "⚠ 본 문서는 AI가 생성한 초안이며, 변호사의 검토 및 수정이 필수입니다.",
                disclaimer_style
            ))

            # Build PDF
            doc.build(story)
            file_buffer.seek(0)

            safe_title = case.title.replace(" ", "_")[:30]
            filename = f"draft_{safe_title}_{draft_response.generated_at.strftime('%Y%m%d')}.pdf"
            content_type = "application/pdf"

            return file_buffer, filename, content_type

        except ImportError:
            raise ValidationError(
                "PDF export is not available. "
                "Please install reportlab: pip install reportlab. "
                "Alternatively, use DOCX format."
            )

    def _register_korean_font(self, pdfmetrics, TTFont) -> bool:
        """
        Register Korean font for PDF generation

        Tries to find and register a Korean font in this order:
        1. Noto Sans KR (bundled or system)
        2. macOS system fonts (AppleGothic, AppleSDGothicNeo)
        3. Linux system fonts (NanumGothic)
        4. Windows system fonts (Malgun Gothic)

        Args:
            pdfmetrics: reportlab pdfmetrics module
            TTFont: reportlab TTFont class

        Returns:
            bool: True if Korean font was registered, False otherwise
        """
        import os

        # Font search paths
        font_candidates = [
            # Bundled font (if exists in project)
            os.path.join(os.path.dirname(__file__), "..", "fonts", "NotoSansKR-Regular.ttf"),
            # macOS system fonts
            "/System/Library/Fonts/AppleSDGothicNeo.ttc",
            "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
            "/Library/Fonts/NotoSansKR-Regular.ttf",
            # Linux system fonts
            "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            # Windows system fonts
            "C:/Windows/Fonts/malgun.ttf",
            "C:/Windows/Fonts/NotoSansKR-Regular.ttf",
        ]

        for font_path in font_candidates:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont("NotoSansKR", font_path))
                    return True
                except Exception:
                    continue

        # No Korean font found - will use default font
        return False

    # ============================================
    # Draft CRUD Operations
    # ============================================

    def list_drafts(self, case_id: str, user_id: str) -> List[DraftListItem]:
        """
        List all drafts for a case

        Args:
            case_id: Case ID
            user_id: User ID requesting drafts

        Returns:
            List of draft summaries

        Raises:
            PermissionError: User does not have access (also for non-existent cases)
        """
        # Check permission first to prevent information leakage
        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("You do not have access to this case")

        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

        # Query drafts for case
        drafts = self.db.query(DraftDocument).filter(
            DraftDocument.case_id == case_id
        ).order_by(DraftDocument.updated_at.desc()).all()

        return [
            DraftListItem(
                id=d.id,
                case_id=d.case_id,
                title=d.title,
                document_type=d.document_type.value,
                version=d.version,
                status=d.status.value,
                updated_at=d.updated_at
            ) for d in drafts
        ]

    def get_draft(self, case_id: str, draft_id: str, user_id: str) -> DraftResponse:
        """
        Get a specific draft by ID

        Args:
            case_id: Case ID
            draft_id: Draft ID
            user_id: User ID requesting draft

        Returns:
            Draft response with full content

        Raises:
            PermissionError: User does not have access (also for non-existent cases)
            NotFoundError: Draft not found
        """
        # Check permission first to prevent information leakage
        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("You do not have access to this case")

        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

        # Get draft
        draft = self.db.query(DraftDocument).filter(
            DraftDocument.id == draft_id,
            DraftDocument.case_id == case_id
        ).first()

        if not draft:
            raise NotFoundError("Draft")

        return DraftResponse(
            id=draft.id,
            case_id=draft.case_id,
            title=draft.title,
            document_type=draft.document_type.value,
            content=draft.content,
            version=draft.version,
            status=draft.status.value,
            created_by=draft.created_by,
            created_at=draft.created_at,
            updated_at=draft.updated_at
        )

    def create_draft(
        self,
        case_id: str,
        draft_data: DraftCreate,
        user_id: str
    ) -> DraftResponse:
        """
        Create a new draft document

        Args:
            case_id: Case ID
            draft_data: Draft creation data
            user_id: User ID creating draft

        Returns:
            Created draft response

        Raises:
            PermissionError: User does not have write access (also for non-existent cases)
        """
        # Check permission first to prevent information leakage
        if not self.member_repo.has_write_access(case_id, user_id):
            raise PermissionError("You do not have write access to this case")

        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

        # Map schema document type to model enum
        doc_type_map = {
            "complaint": DocumentType.COMPLAINT,
            "motion": DocumentType.MOTION,
            "brief": DocumentType.BRIEF,
            "response": DocumentType.RESPONSE,
        }

        # Create draft
        draft = DraftDocument(
            case_id=case_id,
            title=draft_data.title,
            document_type=doc_type_map.get(draft_data.document_type.value, DocumentType.BRIEF),
            content=draft_data.content.model_dump() if draft_data.content else {},
            version=1,
            status=DraftStatus.DRAFT,
            created_by=user_id
        )

        self.db.add(draft)
        self.db.commit()
        self.db.refresh(draft)

        return DraftResponse(
            id=draft.id,
            case_id=draft.case_id,
            title=draft.title,
            document_type=draft.document_type.value,
            content=draft.content,
            version=draft.version,
            status=draft.status.value,
            created_by=draft.created_by,
            created_at=draft.created_at,
            updated_at=draft.updated_at
        )

    def update_draft(
        self,
        case_id: str,
        draft_id: str,
        update_data: DraftUpdate,
        user_id: str
    ) -> DraftResponse:
        """
        Update an existing draft document

        Args:
            case_id: Case ID
            draft_id: Draft ID
            update_data: Draft update data
            user_id: User ID updating draft

        Returns:
            Updated draft response

        Raises:
            PermissionError: User does not have write access (also for non-existent cases)
            NotFoundError: Draft not found
        """
        # Check permission first to prevent information leakage
        if not self.member_repo.has_write_access(case_id, user_id):
            raise PermissionError("You do not have write access to this case")

        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

        # Get draft
        draft = self.db.query(DraftDocument).filter(
            DraftDocument.id == draft_id,
            DraftDocument.case_id == case_id
        ).first()

        if not draft:
            raise NotFoundError("Draft")

        # Map schema document type to model enum
        doc_type_map = {
            "complaint": DocumentType.COMPLAINT,
            "motion": DocumentType.MOTION,
            "brief": DocumentType.BRIEF,
            "response": DocumentType.RESPONSE,
        }

        # Map schema status to model enum
        status_map = {
            "draft": DraftStatus.DRAFT,
            "reviewed": DraftStatus.REVIEWED,
            "exported": DraftStatus.EXPORTED,
        }

        # Update fields if provided
        if update_data.title is not None:
            draft.title = update_data.title

        if update_data.document_type is not None:
            draft.document_type = doc_type_map.get(
                update_data.document_type.value,
                draft.document_type
            )

        if update_data.content is not None:
            draft.content = update_data.content.model_dump()
            # Increment version when content changes
            draft.version += 1

        if update_data.status is not None:
            draft.status = status_map.get(
                update_data.status.value,
                draft.status
            )

        self.db.commit()
        self.db.refresh(draft)

        return DraftResponse(
            id=draft.id,
            case_id=draft.case_id,
            title=draft.title,
            document_type=draft.document_type.value,
            content=draft.content,
            version=draft.version,
            status=draft.status.value,
            created_by=draft.created_by,
            created_at=draft.created_at,
            updated_at=draft.updated_at
        )

    def save_generated_draft(
        self,
        case_id: str,
        draft_response: DraftPreviewResponse,
        user_id: str
    ) -> DraftResponse:
        """
        Save a generated draft preview to the database

        This method converts the ephemeral DraftPreviewResponse into
        a persisted DraftDocument that can be edited and exported.

        Args:
            case_id: Case ID
            draft_response: Generated draft preview response
            user_id: User ID saving the draft

        Returns:
            Saved draft response

        Raises:
            PermissionError: User does not have write access (also for non-existent cases)
        """
        # Check permission first to prevent information leakage
        if not self.member_repo.has_write_access(case_id, user_id):
            raise PermissionError("You do not have write access to this case")

        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

        # Build content structure from draft preview
        content = {
            "header": {
                "court_name": "",
                "case_number": "",
                "parties": {}
            },
            "sections": [
                {
                    "title": "본문",
                    "content": draft_response.draft_text,
                    "order": 1
                }
            ],
            "citations": [
                {
                    "evidence_id": c.evidence_id,
                    "snippet": c.snippet,
                    "labels": c.labels
                } for c in draft_response.citations
            ],
            "footer": {
                "date": draft_response.generated_at.strftime("%Y년 %m월 %d일"),
                "attorney": ""
            }
        }

        # Create draft
        draft = DraftDocument(
            case_id=case_id,
            title=f"{case.title} - 초안",
            document_type=DocumentType.BRIEF,
            content=content,
            version=1,
            status=DraftStatus.DRAFT,
            created_by=user_id
        )

        self.db.add(draft)
        self.db.commit()
        self.db.refresh(draft)

        return DraftResponse(
            id=draft.id,
            case_id=draft.case_id,
            title=draft.title,
            document_type=draft.document_type.value,
            content=draft.content,
            version=draft.version,
            status=draft.status.value,
            created_by=draft.created_by,
            created_at=draft.created_at,
            updated_at=draft.updated_at
        )

    # ==========================================================================
    # Line-Based Template Methods (Phase: 라인별 JSON 템플릿)
    # ==========================================================================

    def load_line_based_template(self, template_type: str) -> dict:
        """
        Load line-based template from Qdrant

        Args:
            template_type: Template type (e.g., "이혼소장")

        Returns:
            Template dict with lines array

        Raises:
            NotFoundError: Template not found
        """
        template = get_template_by_type(template_type)
        if not template:
            raise NotFoundError(f"Template '{template_type}' not found")
        return template

    def fill_placeholders(
        self,
        template_lines: List[dict],
        case_data: dict
    ) -> List[dict]:
        """
        Fill placeholders in template lines with case data

        Placeholders use {{placeholder_key}} format.
        Supports multiple placeholders per line.

        Args:
            template_lines: List of line dicts from template
            case_data: Dict mapping placeholder keys to values

        Returns:
            New list of lines with placeholders replaced
        """
        import re
        import copy

        filled_lines = []
        for line in template_lines:
            new_line = copy.deepcopy(line)
            text = new_line.get("text", "")

            # Find all {{placeholder}} patterns
            placeholders = re.findall(r'\{\{([^}]+)\}\}', text)

            for placeholder in placeholders:
                # Try placeholder_key first, then Korean text
                value = case_data.get(
                    line.get("placeholder_key", ""),
                    case_data.get(placeholder, "")
                )

                if value:
                    text = text.replace(f"{{{{{placeholder}}}}}", str(value))
                elif not value and not case_data:
                    # Keep placeholder or mark as empty
                    text = text.replace(f"{{{{{placeholder}}}}}", "[미입력]")

            new_line["text"] = text
            filled_lines.append(new_line)

        return filled_lines

    def filter_conditional_lines(
        self,
        template_lines: List[dict],
        case_conditions: dict
    ) -> List[dict]:
        """
        Filter template lines based on conditions

        Lines with 'condition' field are only included if the
        corresponding condition in case_conditions is True.
        Lines without 'condition' field are always included.

        Args:
            template_lines: List of line dicts from template
            case_conditions: Dict mapping condition names to booleans

        Returns:
            Filtered list of lines
        """
        filtered = []
        for line in template_lines:
            condition = line.get("condition")
            if condition is None:
                # No condition - always include
                filtered.append(line)
            elif case_conditions.get(condition, False):
                # Condition exists and is True
                filtered.append(line)
            # else: condition is False, skip line

        return filtered

    def fill_ai_generated_content(
        self,
        template_lines: List[dict],
        evidence_context: List[dict],
        case_id: str
    ) -> List[dict]:
        """
        Generate AI content for placeholders marked as ai_generated

        Only processes lines where ai_generated=True.
        Uses GPT-4o to generate appropriate content based on evidence.

        Args:
            template_lines: List of line dicts
            evidence_context: Evidence data for context
            case_id: Case ID for RAG

        Returns:
            Lines with AI-generated content filled in
        """
        import copy

        filled_lines = []
        for line in template_lines:
            new_line = copy.deepcopy(line)

            if line.get("ai_generated", False) and line.get("is_placeholder", False):
                placeholder_key = line.get("placeholder_key", "")
                section = line.get("section", "general")

                # Build prompt for this specific placeholder
                prompt = self._build_ai_placeholder_prompt(
                    placeholder_key,
                    section,
                    evidence_context
                )

                # Generate content
                ai_content = generate_chat_completion(prompt)
                new_line["text"] = ai_content

            filled_lines.append(new_line)

        return filled_lines

    def _build_ai_placeholder_prompt(
        self,
        placeholder_key: str,
        section: str,
        evidence_context: List[dict]
    ) -> List[dict]:
        """Build prompt for AI placeholder generation"""
        evidence_text = self._format_evidence_context(evidence_context)

        system_prompt = """당신은 한국 가정법 전문 법률가입니다.
소장의 특정 부분을 작성해야 합니다.
증거 자료를 바탕으로 법적으로 정확하고 간결한 내용을 작성하세요.
- 증거를 인용할 때는 "갑 제N호증"으로 표기
- 민법 제840조 이혼 사유에 맞는 법률 용어 사용
- 문장은 완결형으로, 불필요한 수식어 제외"""

        section_guides = {
            "청구취지_내용": "청구취지를 작성하세요. 원고가 피고에게 요청하는 사항을 명확히 기재.",
            "청구원인_내용": "청구원인을 작성하세요. 이혼 사유와 그 근거를 증거와 함께 서술.",
            "grounds_content": "청구원인의 핵심 내용을 작성하세요.",
            "claims_content": "청구취지의 핵심 내용을 작성하세요."
        }

        guide = section_guides.get(placeholder_key, f"{placeholder_key} 내용을 작성하세요.")

        user_prompt = f"""## 작성 대상
{guide}

## 증거 자료
{evidence_text}

## 지침
- 증거에 기반한 사실만 기술
- 간결하고 법적으로 정확하게 작성
- 2-3문장 이내로 작성"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

    def render_lines_to_text(self, lines: List[dict]) -> str:
        """
        Render line-based JSON to formatted plain text

        Applies indentation and spacing from format info.

        Args:
            lines: List of line dicts with format info

        Returns:
            Formatted text string
        """
        output_lines = []

        for line in lines:
            text = line.get("text", "")
            fmt = line.get("format", {})

            # Apply indentation
            indent = fmt.get("indent", 0)
            if indent > 0:
                text = " " * indent + text

            output_lines.append(text)

            # Apply spacing after
            spacing_after = fmt.get("spacing_after", 0)
            for _ in range(spacing_after):
                output_lines.append("")

        return "\n".join(output_lines)

    def generate_line_based_draft(
        self,
        case_id: str,
        user_id: str,
        case_data: dict,
        template_type: str = "이혼소장"
    ) -> dict:
        """
        Generate draft using line-based template

        Full pipeline:
        1. Load template from Qdrant
        2. Filter conditional lines
        3. Fill static placeholders
        4. Generate AI content for ai_generated placeholders
        5. Return structured result

        Args:
            case_id: Case ID
            user_id: User ID
            case_data: Data for placeholders
            template_type: Template type to use

        Returns:
            Dict with lines and metadata
        """
        # Validate access
        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("You do not have access to this case")

        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

        # 1. Load template
        template = self.load_line_based_template(template_type)
        lines = template.get("lines", [])

        # 2. Determine conditions from case data
        case_conditions = {
            "has_children": case_data.get("has_children", False),
            "has_alimony": case_data.get("has_alimony", False),
            "has_property": case_data.get("has_property", False)
        }

        # 3. Filter conditional lines
        lines = self.filter_conditional_lines(lines, case_conditions)

        # 4. Fill static placeholders
        lines = self.fill_placeholders(lines, case_data)

        # 5. Get evidence for AI generation
        evidence = get_evidence_by_case(case_id)
        done_evidence = [e for e in evidence if e.get("status") == "done"]

        # 6. Fill AI-generated content
        if done_evidence:
            rag_results = search_evidence_by_semantic(
                case_id=case_id,
                query="이혼 귀책사유 증거",
                top_k=5
            )
            lines = self.fill_ai_generated_content(lines, rag_results, case_id)

        return {
            "case_id": case_id,
            "template_type": template_type,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "lines": lines
        }

    def generate_docx_from_lines(
        self,
        case,
        lines: List[dict]
    ) -> Tuple[BytesIO, str, str]:
        """
        Generate DOCX directly from line-based JSON

        Args:
            case: Case object
            lines: List of line dicts with format info

        Returns:
            Tuple of (file_buffer, filename, content_type)
        """
        if not DOCX_AVAILABLE:
            raise ValidationError("DOCX export is not available. Please install python-docx.")

        doc = Document()

        for line in lines:
            text = line.get("text", "")
            fmt = line.get("format", {})

            # Skip empty lines (just add spacing)
            if not text:
                doc.add_paragraph("")
                continue

            para = doc.add_paragraph()

            # Apply alignment
            align = fmt.get("align", "left")
            if align == "center":
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif align == "right":
                para.alignment = WD_ALIGN_PARAGRAPH.RIGHT

            # Add text with formatting
            run = para.add_run(text)

            if fmt.get("bold", False):
                run.bold = True

            font_size = fmt.get("font_size", 12)
            run.font.size = Pt(font_size)

            # Handle indent as paragraph format
            indent = fmt.get("indent", 0)
            if indent > 0:
                para.paragraph_format.left_indent = Pt(indent * 6)  # 6pt per char approx

        # Save to buffer
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"draft_{case.title[:20]}_{timestamp}.docx"
        content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

        return buffer, filename, content_type

    def generate_pdf_from_lines(
        self,
        case,
        lines: List[dict]
    ) -> Tuple[BytesIO, str, str]:
        """
        Generate PDF directly from line-based JSON

        Args:
            case: Case object
            lines: List of line dicts with format info

        Returns:
            Tuple of (file_buffer, filename, content_type)
        """
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
        except ImportError:
            raise ValidationError("PDF export is not available. Please install reportlab.")

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)

        # Register Korean font
        self._register_korean_font(pdfmetrics, TTFont)

        styles = getSampleStyleSheet()

        # Create custom styles
        style_left = ParagraphStyle('Left', parent=styles['Normal'], alignment=TA_LEFT)
        style_center = ParagraphStyle('Center', parent=styles['Normal'], alignment=TA_CENTER)
        style_right = ParagraphStyle('Right', parent=styles['Normal'], alignment=TA_RIGHT)

        story = []

        for line in lines:
            text = line.get("text", "")
            fmt = line.get("format", {})

            if not text:
                story.append(Spacer(1, 12))
                continue

            # Choose style based on alignment
            align = fmt.get("align", "left")
            if align == "center":
                style = style_center
            elif align == "right":
                style = style_right
            else:
                style = style_left

            # Apply bold if needed
            if fmt.get("bold", False):
                text = f"<b>{text}</b>"

            # Apply indent
            indent = fmt.get("indent", 0)
            if indent > 0:
                text = "&nbsp;" * indent + text

            para = Paragraph(text, style)
            story.append(para)

            # Add spacing
            spacing = fmt.get("spacing_after", 0)
            if spacing > 0:
                story.append(Spacer(1, spacing * 12))

        doc.build(story)
        buffer.seek(0)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"draft_{case.title[:20]}_{timestamp}.pdf"
        content_type = "application/pdf"

        return buffer, filename, content_type
