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

from app.db.schemas import (
    DraftPreviewRequest,
    DraftPreviewResponse,
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
    get_template_by_type,
    search_evidence_by_semantic,
)
from app.utils.openai_client import generate_chat_completion
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
        # 1. Validate case access
        if not self.member_repo.has_access(case_id, user_id):
            raise PermissionError("You do not have access to this case")

        case = self.case_repo.get_by_id(case_id)
        if not case:
            raise NotFoundError("Case")

        # 2. Retrieve evidence metadata from DynamoDB
        evidence_list = get_evidence_by_case(case_id)

        if not evidence_list:
            raise ValidationError("사건에 증거가 하나도 없습니다. 증거를 업로드한 후 초안을 생성해 주세요.")

        # 3. Perform semantic RAG search in Qdrant (evidence + legal)
        rag_results = self.rag_orchestrator.perform_rag_search(case_id, request.sections)
        evidence_results = rag_results.get("evidence", [])
        legal_results = rag_results.get("legal", [])

        # 3.5 Search similar precedents
        precedent_results = self.rag_orchestrator.search_precedents(case_id)

        # 4. Check if template exists for JSON output mode
        template = get_template_by_type("이혼소장")
        use_json_output = template is not None

        # 5. Build GPT-4o prompt with RAG context + precedents
        prompt_messages = self.prompt_builder.build_draft_prompt(
            case=case,
            sections=request.sections,
            evidence_context=evidence_results,
            legal_context=legal_results,
            precedent_context=precedent_results,
            language=request.language,
            style=request.style
        )

        # 6. Generate draft using GPT-4o-mini (faster response, optimized for 30s API Gateway limit)
        raw_response = generate_chat_completion(
            messages=prompt_messages,
            model="gpt-4o-mini",
            temperature=0.3,
            max_tokens=2000
        )

        # 7. Process response based on output mode
        if use_json_output:
            renderer = DocumentRenderer()
            json_doc = renderer.parse_json_response(raw_response)

            if json_doc:
                draft_text = renderer.render_to_text(json_doc)
            else:
                draft_text = raw_response
        else:
            draft_text = raw_response

        # 8. Extract citations from RAG results
        citations = self.citation_extractor.extract_evidence_citations(evidence_results)

        # 8.5 Extract precedent citations
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

    def _build_draft_prompt(self, case, sections, evidence_context, legal_context, precedent_context, language, style) -> List[dict]:
        """Legacy: delegates to PromptBuilder"""
        return self.prompt_builder.build_draft_prompt(
            case, sections, evidence_context, legal_context, precedent_context, language, style
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
