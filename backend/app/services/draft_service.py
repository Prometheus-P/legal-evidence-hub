"""
Draft Service - Business logic for draft generation with RAG
Orchestrates Qdrant RAG + OpenAI GPT-4o for draft preview

Refactored in Issue #325: Split into modular components
- RAGOrchestrator: RAG search and context formatting
- PromptBuilder: GPT-4o prompt construction
- CitationExtractor: Citation parsing and extraction
- DocumentExporter: DOCX/PDF generation
- LineTemplateService: Line-based template processing
"""

from sqlalchemy.orm import Session
from typing import List, Tuple
from datetime import datetime, timezone
from io import BytesIO
import json
import logging
import traceback

from fastapi import BackgroundTasks

from app.db.schemas import (
    DraftPreviewRequest,
    DraftPreviewResponse,
    DraftExportFormat,
    DraftCreate,
    DraftUpdate,
    DraftResponse,
    DraftListItem,
    # Async Draft Preview
    DraftJobStatus,
    DraftJobCreateResponse,
    DraftJobStatusResponse,
)
from app.db.models import DraftDocument, DraftStatus, DocumentType, Job, JobType, JobStatus
from app.repositories.case_repository import CaseRepository
from app.repositories.case_member_repository import CaseMemberRepository
from app.utils.dynamo import get_evidence_by_case, get_case_fact_summary
from app.utils.qdrant import (
    get_template_by_type,
    search_evidence_by_semantic,
)
from app.utils.openai_client import generate_chat_completion
from app.utils.gemini_client import generate_chat_completion_gemini
from app.core.config import settings
from app.services.document_renderer import DocumentRenderer
from app.middleware import NotFoundError, PermissionError, ValidationError
from app.services.precedent_service import PrecedentService

# Refactored modular components (Issue #325)
from app.services.draft.rag_orchestrator import RAGOrchestrator
from app.services.draft.prompt_builder import PromptBuilder
from app.services.draft.citation_extractor import CitationExtractor
from app.services.draft.document_exporter import DocumentExporter, DOCX_AVAILABLE
from app.services.draft.line_template_service import LineTemplateService

# Re-export for backward compatibility with tests that patch at module level
# Note: These are imported but used in submodules; re-exporting allows patching
try:
    from docx import Document
except ImportError:
    Document = None

# Re-export search_legal_knowledge with alias for tests
from app.utils.qdrant import search_legal_knowledge

__all__ = [
    'DraftService',
    'generate_chat_completion',
    'get_evidence_by_case',
    'get_template_by_type',
    'search_evidence_by_semantic',
    'search_legal_knowledge',
    'DOCX_AVAILABLE',
    'Document',
]

logger = logging.getLogger(__name__)


class DraftService:
    """
    Service for draft generation with RAG.
    Uses modular components for better separation of concerns.
    """

    def __init__(self, db: Session):
        self.db = db
        self.case_repo = CaseRepository(db)
        self.member_repo = CaseMemberRepository(db)
        self.precedent_service = PrecedentService(db)

        # Initialize modular components
        self.rag_orchestrator = RAGOrchestrator(self.precedent_service)
        self.prompt_builder = PromptBuilder(self.rag_orchestrator)
        self.citation_extractor = CitationExtractor()
        self.document_exporter = DocumentExporter()
        self.line_template_service = LineTemplateService(
            self.rag_orchestrator,
            self.prompt_builder
        )

    def generate_draft_preview(
        self,
        case_id: str,
        request: DraftPreviewRequest,
        user_id: str
    ) -> DraftPreviewResponse:
        """
        Generate draft preview using Fact-Summary + GPT-4o

        Process (016-draft-fact-summary):
        1. Validate case access
        2. Get fact summary context (REQUIRED)
        3. Get legal knowledge and precedents (optional RAG)
        4. Build GPT-4o prompt with fact summary as primary context
        5. Generate draft text
        6. Return with empty citations (no evidence RAG)

        Args:
            case_id: Case ID
            request: Draft generation request (sections, language, style)
            user_id: User ID requesting draft

        Returns:
            Draft preview with citations

        Raises:
            PermissionError: User does not have access (also for non-existent cases)
            ValidationError: No fact summary exists for case
        """
        # 1. Validate case access
        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("You do not have access to this case")

        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

        # 2. Get fact summary context (REQUIRED - 016-draft-fact-summary)
        fact_summary_context = self._get_fact_summary_context(case_id)
        if not fact_summary_context:
            raise ValidationError(
                "사실관계 요약을 먼저 생성해주세요. "
                "[사건 상세] → [사실관계 요약] 탭에서 생성할 수 있습니다."
            )

        # 3. Get legal knowledge (keep RAG for legal references)
        rag_results = self.rag_orchestrator.perform_rag_search(case_id, request.sections)
        legal_results = rag_results.get("legal", [])
        # Skip evidence RAG - use fact summary instead (016-draft-fact-summary)
        evidence_results = []

        # 3.5 Search similar precedents
        precedent_results = self.rag_orchestrator.search_precedents(case_id)

        # 3.6 Search consultation records (Issue #403)
        consultation_results = self.rag_orchestrator.search_case_consultations(case_id)

        # fact_summary_context already retrieved and validated above (016-draft-fact-summary)

        # 4. Check if using Gemini (force text output) or OpenAI (can use JSON)
        use_gemini = settings.USE_GEMINI_FOR_DRAFT and settings.GEMINI_API_KEY

        # 5. Check if template exists for JSON output mode (only for OpenAI)
        template = get_template_by_type("이혼소장")
        use_json_output = template is not None and not use_gemini

        # 6. Build GPT-4o prompt with RAG context + precedents + consultations + fact summary (Issue #403)
        # For Gemini: force_text_output=True to get readable legal document (not JSON)
        prompt_messages = self.prompt_builder.build_draft_prompt(
            case=case,
            sections=request.sections,
            evidence_context=evidence_results,
            legal_context=legal_results,
            precedent_context=precedent_results,
            consultation_context=consultation_results,
            fact_summary_context=fact_summary_context,
            language=request.language,
            style=request.style,
            force_text_output=use_gemini  # Gemini works better with text output
        )

        # 7. Generate draft using Gemini (faster) or GPT-4o-mini (fallback)
        if use_gemini:
            logger.info("[DRAFT] Using Gemini 2.0 Flash for draft generation")
            raw_response = generate_chat_completion_gemini(
                messages=prompt_messages,
                model=settings.GEMINI_MODEL_CHAT,
                temperature=0.3,
                max_tokens=4000
            )
        else:
            logger.info("[DRAFT] Using OpenAI GPT-4o-mini for draft generation")
            raw_response = generate_chat_completion(
                messages=prompt_messages,
                model="gpt-4o-mini",
                temperature=0.3,
                max_tokens=4000
            )

        # 8. Process response based on output mode
        if use_json_output:
            renderer = DocumentRenderer()
            json_doc = renderer.parse_json_response(raw_response)

            if json_doc:
                draft_text = renderer.render_to_text(json_doc)
            else:
                draft_text = raw_response
        else:
            draft_text = raw_response

        # 8.5 Clean up any HTML entities that AI might output as text
        # Double protection in case gemini_client doesn't catch all cases
        draft_text = draft_text.replace('&nbsp;', ' ')

        # 9. Extract citations from RAG results
        citations = self.citation_extractor.extract_evidence_citations(evidence_results)

        # 9.5 Extract precedent citations
        precedent_citations = self.citation_extractor.extract_precedent_citations(precedent_results)

        return DraftPreviewResponse(
            case_id=case_id,
            draft_text=draft_text,
            citations=citations,
            precedent_citations=precedent_citations,
            generated_at=datetime.now(timezone.utc)
        )

    def export_draft(
        self,
        case_id: str,
        user_id: str,
        export_format: DraftExportFormat = DraftExportFormat.DOCX
    ) -> Tuple[BytesIO, str, str]:
        """
        Export draft as DOCX or PDF file

        Args:
            case_id: Case ID
            user_id: User ID requesting export
            export_format: Output format (docx or pdf)

        Returns:
            Tuple of (file_bytes, filename, content_type)

        Raises:
            PermissionError: User does not have access
            ValidationError: Export format not supported
        """
        # Validate case access
        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("You do not have access to this case")

        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

        # Generate draft preview
        request = DraftPreviewRequest()
        draft_response = self.generate_draft_preview(case_id, request, user_id)

        # Convert to requested format
        if export_format == DraftExportFormat.DOCX:
            return self.document_exporter.generate_docx(case, draft_response)
        elif export_format == DraftExportFormat.PDF:
            return self.document_exporter.generate_pdf(case, draft_response)
        else:
            raise ValidationError(f"Unsupported export format: {export_format}")

    # ============================================
    # Draft CRUD Operations
    # ============================================

    def list_drafts(self, case_id: str, user_id: str) -> List[DraftListItem]:
        """List all drafts for a case"""
        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("You do not have access to this case")

        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

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
        """Get a specific draft by ID"""
        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("You do not have access to this case")

        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

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
        """Create a new draft document"""
        if not self.member_repo.has_write_access(case_id, user_id):
            raise PermissionError("You do not have write access to this case")

        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

        doc_type_map = {
            "complaint": DocumentType.COMPLAINT,
            "motion": DocumentType.MOTION,
            "brief": DocumentType.BRIEF,
            "response": DocumentType.RESPONSE,
        }

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
        """Update an existing draft document"""
        if not self.member_repo.has_write_access(case_id, user_id):
            raise PermissionError("You do not have write access to this case")

        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

        draft = self.db.query(DraftDocument).filter(
            DraftDocument.id == draft_id,
            DraftDocument.case_id == case_id
        ).first()

        if not draft:
            raise NotFoundError("Draft")

        doc_type_map = {
            "complaint": DocumentType.COMPLAINT,
            "motion": DocumentType.MOTION,
            "brief": DocumentType.BRIEF,
            "response": DocumentType.RESPONSE,
        }

        status_map = {
            "draft": DraftStatus.DRAFT,
            "reviewed": DraftStatus.REVIEWED,
            "exported": DraftStatus.EXPORTED,
        }

        if update_data.title is not None:
            draft.title = update_data.title

        if update_data.document_type is not None:
            draft.document_type = doc_type_map.get(
                update_data.document_type.value,
                draft.document_type
            )

        if update_data.content is not None:
            draft.content = update_data.content.model_dump()
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
        """Save a generated draft preview to the database"""
        if not self.member_repo.has_write_access(case_id, user_id):
            raise PermissionError("You do not have write access to this case")

        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

        citations_formatted = self.citation_extractor.format_citations_for_document(
            draft_response.citations,
            draft_response.precedent_citations
        )

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
            "citations": citations_formatted.get("evidence", []),
            "footer": {
                "date": draft_response.generated_at.strftime("%Y년 %m월 %d일"),
                "attorney": ""
            }
        }

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
    # Line-Based Template Methods (delegated to LineTemplateService)
    # ==========================================================================

    def load_line_based_template(self, template_type: str) -> dict:
        """Load line-based template from Qdrant"""
        return self.line_template_service.load_template(template_type)

    def fill_placeholders(
        self,
        template_lines: List[dict],
        case_data: dict
    ) -> List[dict]:
        """Fill placeholders in template lines with case data"""
        return self.line_template_service.fill_placeholders(template_lines, case_data)

    def filter_conditional_lines(
        self,
        template_lines: List[dict],
        case_conditions: dict
    ) -> List[dict]:
        """Filter template lines based on conditions"""
        return self.line_template_service.filter_conditional_lines(template_lines, case_conditions)

    def fill_ai_generated_content(
        self,
        template_lines: List[dict],
        evidence_context: List[dict],
        case_id: str
    ) -> List[dict]:
        """Generate AI content for placeholders marked as ai_generated"""
        return self.line_template_service.fill_ai_generated_content(
            template_lines, evidence_context, case_id
        )

    def render_lines_to_text(self, lines: List[dict]) -> str:
        """Render line-based JSON to formatted plain text"""
        return self.line_template_service.render_to_text(lines)

    def generate_line_based_draft(
        self,
        case_id: str,
        user_id: str,
        case_data: dict,
        template_type: str = "이혼소장"
    ) -> dict:
        """Generate draft using line-based template"""
        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("You do not have access to this case")

        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

        return self.line_template_service.generate_draft(
            case_id, case, case_data, template_type
        )

    def generate_docx_from_lines(
        self,
        case,
        lines: List[dict]
    ) -> Tuple[BytesIO, str, str]:
        """Generate DOCX directly from line-based JSON"""
        return self.document_exporter.generate_docx_from_lines(case, lines)

    def generate_pdf_from_lines(
        self,
        case,
        lines: List[dict]
    ) -> Tuple[BytesIO, str, str]:
        """Generate PDF directly from line-based JSON"""
        return self.document_exporter.generate_pdf_from_lines(case, lines)

    # ==========================================================================
    # Legacy methods for backward compatibility (delegates to components)
    # ==========================================================================

    def _perform_rag_search(self, case_id: str, sections: List[str]) -> dict:
        """Legacy: delegates to RAGOrchestrator"""
        return self.rag_orchestrator.perform_rag_search(case_id, sections)

    def _search_precedents_for_draft(self, case_id: str) -> List[dict]:
        """Legacy: delegates to RAGOrchestrator"""
        return self.rag_orchestrator.search_precedents(case_id)

    def _format_evidence_context(self, evidence_results: List[dict]) -> str:
        """Legacy: delegates to RAGOrchestrator"""
        return self.rag_orchestrator.format_evidence_context(evidence_results)

    def _format_legal_context(self, legal_results: List[dict]) -> str:
        """Legacy: delegates to RAGOrchestrator"""
        return self.rag_orchestrator.format_legal_context(legal_results)

    def _format_precedent_context(self, precedent_results: List[dict]) -> str:
        """Legacy: delegates to RAGOrchestrator"""
        return self.rag_orchestrator.format_precedent_context(precedent_results)

    def _format_rag_context(self, rag_results: List[dict]) -> str:
        """Legacy: delegates to RAGOrchestrator"""
        return self.rag_orchestrator.format_rag_context(rag_results)

    def _extract_citations(self, rag_results: List[dict]) -> List:
        """Legacy: delegates to CitationExtractor"""
        return self.citation_extractor.extract_evidence_citations(rag_results)

    def _extract_precedent_citations(self, precedent_results: List[dict]) -> List:
        """Legacy: delegates to CitationExtractor"""
        return self.citation_extractor.extract_precedent_citations(precedent_results)

    def _build_draft_prompt(self, case, sections, evidence_context, legal_context, precedent_context, fact_summary_context="", language="ko", style="formal") -> List[dict]:
        """Legacy: delegates to PromptBuilder"""
        return self.prompt_builder.build_draft_prompt(
            case, sections, evidence_context, legal_context, precedent_context, fact_summary_context, language, style
        )

    def _build_ai_placeholder_prompt(self, placeholder_key, section, evidence_context) -> List[dict]:
        """Legacy: delegates to PromptBuilder"""
        return self.prompt_builder.build_ai_placeholder_prompt(
            placeholder_key, section, evidence_context
        )

    def _generate_docx(self, case, draft_response) -> Tuple[BytesIO, str, str]:
        """Legacy: delegates to DocumentExporter"""
        return self.document_exporter.generate_docx(case, draft_response)

    def _generate_pdf(self, case, draft_response) -> Tuple[BytesIO, str, str]:
        """Legacy: delegates to DocumentExporter"""
        return self.document_exporter.generate_pdf(case, draft_response)

    def _register_korean_font(self, pdfmetrics, TTFont) -> bool:
        """Legacy: delegates to DocumentExporter"""
        return self.document_exporter._register_korean_font(pdfmetrics, TTFont)

    def _get_fact_summary_context(self, case_id: str) -> str:
        """
        Get fact summary context for draft generation (014-case-fact-summary T023)

        Retrieves stored fact summary (lawyer-modified version preferred, AI-generated as fallback).
        Returns empty string if no summary exists.

        Args:
            case_id: Case ID

        Returns:
            Fact summary text for context injection, empty string if not available
        """
        try:
            summary_data = get_case_fact_summary(case_id)
            if not summary_data:
                return ""

            # Prefer lawyer-modified summary over AI-generated
            fact_summary = summary_data.get("modified_summary") or summary_data.get("ai_summary", "")
            if not fact_summary:
                return ""

            return f"""[사건 사실관계 요약]
{fact_summary}
---
위 사실관계는 변호사가 검토/수정한 내용입니다. 초안 작성 시 이 사실관계를 우선적으로 참조하세요."""
        except Exception:
            # Silently fail - fact summary is optional context
            return ""

    # ==========================================================================
    # Async Draft Preview Methods (API Gateway 30s timeout 우회)
    # ==========================================================================

    def start_async_draft_preview(
        self,
        case_id: str,
        request: DraftPreviewRequest,
        user_id: str,
        background_tasks: BackgroundTasks
    ) -> DraftJobCreateResponse:
        """
        비동기 초안 생성 시작

        1. Job 레코드 생성 (status: QUEUED)
        2. BackgroundTask로 초안 생성 시작
        3. 즉시 job_id 반환
        """
        # 1. Validate case access
        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("You do not have access to this case")

        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

        # 2. Create job record
        job = Job(
            case_id=case_id,
            user_id=user_id,
            job_type=JobType.DRAFT_GENERATION,
            status=JobStatus.QUEUED,
            input_data=json.dumps({
                "sections": request.sections,
                "language": request.language,
                "style": request.style
            })
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        # 3. Schedule background task
        # BackgroundTask는 request lifecycle 이후에 실행되므로
        # 새로운 DB 세션을 생성해야 함
        background_tasks.add_task(
            self._execute_draft_generation_task,
            job.id,
            case_id,
            request.sections,
            request.language,
            request.style,
            user_id
        )

        return DraftJobCreateResponse(
            job_id=job.id,
            case_id=case_id,
            status=DraftJobStatus.QUEUED,
            created_at=job.created_at
        )

    def _execute_draft_generation_task(
        self,
        job_id: str,
        case_id: str,
        sections: List[str],
        language: str,
        style: str,
        user_id: str
    ):
        """
        백그라운드에서 초안 생성 실행

        Note: BackgroundTask에서는 새 DB 세션을 사용해야 함
        """
        from app.db.session import SessionLocal

        db = SessionLocal()
        try:
            # 1. Update job status to PROCESSING
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                logger.error(f"Job {job_id} not found")
                return

            job.status = JobStatus.PROCESSING
            job.started_at = datetime.now(timezone.utc)
            job.progress = "10"
            db.commit()

            # 2. Re-initialize service with new DB session
            draft_service = DraftService(db)

            # 3. Create request object
            request = DraftPreviewRequest(
                sections=sections,
                language=language,
                style=style
            )

            # 4. Generate draft (this is the slow part)
            logger.info(f"Starting draft generation for job {job_id}")
            job.progress = "30"
            db.commit()

            draft_response = draft_service.generate_draft_preview(
                case_id=case_id,
                request=request,
                user_id=user_id
            )

            job.progress = "90"
            db.commit()

            # 5. Store result
            job.status = JobStatus.COMPLETED
            job.progress = "100"
            job.completed_at = datetime.now(timezone.utc)
            job.output_data = json.dumps({
                "case_id": draft_response.case_id,
                "draft_text": draft_response.draft_text,
                "citations": [c.model_dump() for c in draft_response.citations],
                "precedent_citations": [p.model_dump() for p in draft_response.precedent_citations],
                "generated_at": draft_response.generated_at.isoformat(),
                "preview_disclaimer": draft_response.preview_disclaimer
            })
            db.commit()

            logger.info(f"Draft generation completed for job {job_id}")

        except Exception as e:
            logger.error(f"Draft generation failed for job {job_id}: {e}")
            logger.error(traceback.format_exc())

            # Update job with error
            try:
                job = db.query(Job).filter(Job.id == job_id).first()
                if job:
                    job.status = JobStatus.FAILED
                    job.completed_at = datetime.now(timezone.utc)
                    job.error_details = json.dumps({
                        "error": str(e),
                        "traceback": traceback.format_exc()
                    })
                    db.commit()
            except Exception as commit_error:
                logger.error(f"Failed to update job status: {commit_error}")
        finally:
            db.close()

    def get_draft_job_status(
        self,
        case_id: str,
        job_id: str,
        user_id: str
    ) -> DraftJobStatusResponse:
        """
        비동기 초안 생성 작업 상태 조회
        """
        # 1. Validate case access
        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("You do not have access to this case")

        # 2. Get job
        job = self.db.query(Job).filter(
            Job.id == job_id,
            Job.case_id == case_id,
            Job.job_type == JobType.DRAFT_GENERATION
        ).first()

        if not job:
            raise NotFoundError("Draft job")

        # 3. Convert to response
        status_map = {
            JobStatus.QUEUED: DraftJobStatus.QUEUED,
            JobStatus.PROCESSING: DraftJobStatus.PROCESSING,
            JobStatus.COMPLETED: DraftJobStatus.COMPLETED,
            JobStatus.FAILED: DraftJobStatus.FAILED,
            JobStatus.RETRY: DraftJobStatus.QUEUED,
            JobStatus.CANCELLED: DraftJobStatus.FAILED,
        }

        # Parse result if completed
        result = None
        if job.status == JobStatus.COMPLETED and job.output_data:
            try:
                output = json.loads(job.output_data)
                result = DraftPreviewResponse(
                    case_id=output["case_id"],
                    draft_text=output["draft_text"],
                    citations=output["citations"],
                    precedent_citations=output.get("precedent_citations", []),
                    generated_at=datetime.fromisoformat(output["generated_at"]),
                    preview_disclaimer=output.get("preview_disclaimer", "")
                )
            except Exception as e:
                logger.error(f"Failed to parse job output: {e}")

        # Parse error if failed
        error_message = None
        if job.status == JobStatus.FAILED and job.error_details:
            try:
                error = json.loads(job.error_details)
                error_message = error.get("error", "알 수 없는 오류가 발생했습니다.")
            except Exception:
                error_message = "알 수 없는 오류가 발생했습니다."

        return DraftJobStatusResponse(
            job_id=job.id,
            case_id=job.case_id,
            status=status_map.get(job.status, DraftJobStatus.QUEUED),
            progress=int(job.progress) if job.progress else 0,
            result=result,
            error_message=error_message,
            created_at=job.created_at,
            completed_at=job.completed_at
        )
