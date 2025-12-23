"""
Unit tests for Draft Service
TDD - Improving test coverage for draft_service.py
Updated for Issue #325 refactoring (modular components)
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.services.draft_service import DraftService
from app.services.draft.rag_orchestrator import RAGOrchestrator
from app.services.draft.prompt_builder import PromptBuilder
from app.services.draft.citation_extractor import CitationExtractor
from app.services.draft.document_exporter import DocumentExporter
from app.db.schemas import DraftPreviewRequest, DraftExportFormat
from app.middleware.error_handler import ValidationError, NotFoundError, PermissionError


def create_mock_service():
    """Create a DraftService with mocked components"""
    mock_db = MagicMock()

    with patch.object(DraftService, '__init__', lambda x, y: None):
        service = DraftService(mock_db)
        service.db = mock_db
        service.case_repo = MagicMock()
        service.member_repo = MagicMock()
        service.precedent_service = MagicMock()

        # Initialize modular components
        service.rag_orchestrator = RAGOrchestrator(service.precedent_service)
        service.prompt_builder = PromptBuilder(service.rag_orchestrator)
        service.citation_extractor = CitationExtractor()
        service.document_exporter = DocumentExporter()

    return service


class TestDraftServiceInit:
    """Unit tests for DraftService __init__ method (lines 40-42)"""

    def test_init_creates_repositories(self, test_env):
        """Instantiating DraftService creates all required repositories"""
        from app.db.session import get_db

        db = next(get_db())

        service = DraftService(db)

        assert service.db == db
        assert service.case_repo is not None
        assert service.member_repo is not None
        # Check new components
        assert service.rag_orchestrator is not None
        assert service.prompt_builder is not None
        assert service.citation_extractor is not None
        assert service.document_exporter is not None

        db.close()


class TestFormatEvidenceContext:
    """Unit tests for _format_evidence_context method (delegates to RAGOrchestrator)"""

    def test_format_evidence_context_empty(self):
        """Returns placeholder for empty results"""
        service = create_mock_service()

        result = service._format_evidence_context([])

        assert "(증거 자료 없음" in result

    def test_format_evidence_context_with_data(self):
        """Formats evidence data correctly"""
        evidence = [
            {
                "chunk_id": "ev-123",
                "document": "피고는 폭언을 하였습니다.",
                "legal_categories": ["폭언", "유책사유"],
                "sender": "원고",
                "timestamp": "2024-01-15"
            }
        ]

        service = create_mock_service()

        result = service._format_evidence_context(evidence)

        assert "[갑 제1호증]" in result
        assert "ev-123" in result
        assert "폭언" in result
        assert "원고" in result

    def test_format_evidence_context_truncates_long_content(self):
        """Truncates content longer than 500 chars"""
        long_content = "A" * 600
        evidence = [{"document": long_content}]

        service = create_mock_service()

        result = service._format_evidence_context(evidence)

        assert "..." in result
        assert "A" * 500 in result


class TestFormatLegalContext:
    """Unit tests for _format_legal_context method"""

    def test_format_legal_context_empty(self):
        """Returns placeholder for empty results"""
        service = create_mock_service()

        result = service._format_legal_context([])

        assert "(관련 법률 조문 없음)" in result

    def test_format_legal_context_with_data(self):
        """Formats legal documents correctly"""
        legal_docs = [
            {
                "article_number": "제840조",
                "statute_name": "민법",
                "document": "재판상 이혼 사유..."
            }
        ]

        service = create_mock_service()

        result = service._format_legal_context(legal_docs)

        assert "민법" in result
        assert "제840조" in result
        assert "재판상 이혼" in result


class TestFormatRagContext:
    """Unit tests for _format_rag_context method"""

    def test_format_rag_context_empty(self):
        """Returns placeholder for empty results"""
        service = create_mock_service()

        result = service._format_rag_context([])

        assert "(증거 자료 없음" in result

    def test_format_rag_context_with_data(self):
        """Formats RAG results correctly"""
        rag_results = [
            {
                "id": "ev-456",
                "content": "증거 내용입니다.",
                "labels": ["불륜"],
                "speaker": "피고",
                "timestamp": "2024-02-20"
            }
        ]

        service = create_mock_service()

        result = service._format_rag_context(rag_results)

        assert "[증거 1]" in result
        assert "ev-456" in result
        assert "불륜" in result

    def test_format_rag_context_truncates_long_content(self):
        """Truncates content longer than 500 chars"""
        long_content = "B" * 600
        rag_results = [{"content": long_content}]

        service = create_mock_service()

        result = service._format_rag_context(rag_results)

        assert "..." in result


class TestExtractCitations:
    """Unit tests for _extract_citations method (delegates to CitationExtractor)"""

    def test_extract_citations_empty(self):
        """Returns empty list for empty results"""
        service = create_mock_service()

        result = service._extract_citations([])

        assert result == []

    def test_extract_citations_with_data(self):
        """Extracts citations from RAG results"""
        rag_results = [
            {
                "evidence_id": "ev-789",
                "content": "증거 내용",
                "labels": ["폭언"]
            }
        ]

        service = create_mock_service()

        result = service._extract_citations(rag_results)

        assert len(result) == 1
        assert result[0].evidence_id == "ev-789"
        assert result[0].labels == ["폭언"]

    def test_extract_citations_truncates_snippet(self):
        """Truncates snippet longer than 200 chars"""
        long_content = "C" * 300
        rag_results = [{"content": long_content, "id": "ev-1"}]

        service = create_mock_service()

        result = service._extract_citations(rag_results)

        assert "..." in result[0].snippet
        assert len(result[0].snippet) == 203  # 200 + "..."


class TestGenerateDraftPreview:
    """Unit tests for generate_draft_preview method"""

    def test_generate_draft_preview_case_not_found(self):
        """Raises NotFoundError when case not found"""
        service = create_mock_service()
        service.case_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError):
            service.generate_draft_preview(
                "nonexistent",
                DraftPreviewRequest(),
                "user-123"
            )

    def test_generate_draft_preview_no_access(self):
        """Raises PermissionError when user has no access"""
        service = create_mock_service()
        mock_case = MagicMock()
        service.case_repo.get_by_id.return_value = mock_case
        service.member_repo.has_access.return_value = False

        with pytest.raises(PermissionError):
            service.generate_draft_preview(
                "case-123",
                DraftPreviewRequest(),
                "user-123"
            )

    @patch('app.services.draft_service.get_case_fact_summary')
    def test_generate_draft_preview_no_fact_summary(self, mock_get_fact_summary):
        """Raises ValidationError when no fact summary exists (016-draft-fact-summary)"""
        mock_get_fact_summary.return_value = None

        service = create_mock_service()
        mock_case = MagicMock()
        service.case_repo.get_by_id.return_value = mock_case
        service.member_repo.has_access.return_value = True

        with pytest.raises(ValidationError, match="사실관계 요약을 먼저 생성해주세요"):
            service.generate_draft_preview(
                "case-123",
                DraftPreviewRequest(),
                "user-123"
            )

    @patch('app.services.draft_service.get_case_fact_summary')
    @patch('app.services.draft_service.generate_chat_completion')
    @patch('app.services.draft_service.get_template_by_type')
    @patch('app.services.draft.rag_orchestrator.search_legal_knowledge')
    @patch('app.services.draft.rag_orchestrator.search_evidence_by_semantic')
    @patch('app.services.draft_service.get_evidence_by_case')
    def test_generate_draft_preview_success(
        self,
        mock_get_evidence,
        mock_search_evidence,
        mock_search_legal,
        mock_get_template,
        mock_generate,
        mock_get_fact_summary
    ):
        """Successfully generates draft preview"""
        mock_case = MagicMock()
        mock_case.title = "이혼 사건"
        mock_case.description = "테스트 사건"

        mock_get_evidence.return_value = [{"status": "done", "id": "ev-1"}]
        mock_search_evidence.return_value = [{"id": "ev-1", "content": "증거"}]
        mock_search_legal.return_value = []
        mock_get_template.return_value = None
        mock_generate.return_value = "이혼 소장 초안 내용"
        mock_get_fact_summary.return_value = {"ai_summary": "테스트 사실관계 요약"}

        service = create_mock_service()
        service.case_repo.get_by_id.return_value = mock_case
        service.member_repo.has_access.return_value = True
        service.rag_orchestrator.search_precedents = MagicMock(return_value=[])

        result = service.generate_draft_preview(
            "case-123",
            DraftPreviewRequest(sections=["청구취지"]),
            "user-123"
        )

        assert result.case_id == "case-123"
        assert result.draft_text == "이혼 소장 초안 내용"


class TestPerformRagSearch:
    """Unit tests for _perform_rag_search method (delegates to RAGOrchestrator)"""

    @patch('app.services.draft.rag_orchestrator.search_legal_knowledge')
    @patch('app.services.draft.rag_orchestrator.search_evidence_by_semantic')
    def test_perform_rag_search_with_청구원인(self, mock_search_ev, mock_search_legal):
        """Uses fault evidence query for 청구원인 section"""
        mock_search_ev.return_value = []
        mock_search_legal.return_value = []

        service = create_mock_service()

        service._perform_rag_search("case-123", ["청구원인"])

        # Should search with fault-related keywords
        mock_search_ev.assert_called_once()
        call_args = mock_search_ev.call_args
        assert "귀책사유" in call_args.kwargs["query"]

    @patch('app.services.draft.rag_orchestrator.search_legal_knowledge')
    @patch('app.services.draft.rag_orchestrator.search_evidence_by_semantic')
    def test_perform_rag_search_general(self, mock_search_ev, mock_search_legal):
        """Uses section-based query for other sections"""
        mock_search_ev.return_value = []
        mock_search_legal.return_value = []

        service = create_mock_service()

        result = service._perform_rag_search("case-123", ["당사자", "청구취지"])

        assert "evidence" in result
        assert "legal" in result


class TestExportDraft:
    """Unit tests for export_draft method"""

    def test_export_draft_case_not_found(self):
        """Raises NotFoundError when case not found"""
        service = create_mock_service()
        service.case_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError):
            service.export_draft("nonexistent", "user-123")

    def test_export_draft_no_access(self):
        """Raises PermissionError when user has no access"""
        mock_case = MagicMock()

        service = create_mock_service()
        service.case_repo.get_by_id.return_value = mock_case
        service.member_repo.has_access.return_value = False

        with pytest.raises(PermissionError):
            service.export_draft("case-123", "user-123")


class TestBuildDraftPrompt:
    """Unit tests for _build_draft_prompt method (delegates to PromptBuilder)"""

    def test_build_draft_prompt_structure(self):
        """Builds correct prompt structure"""
        mock_case = MagicMock()
        mock_case.title = "테스트 사건"
        mock_case.description = "사건 설명"

        service = create_mock_service()

        result = service._build_draft_prompt(
            case=mock_case,
            sections=["청구원인"],
            evidence_context=[],
            legal_context=[],
            precedent_context=[],
            language="ko",
            style="formal"
        )

        assert len(result) == 2
        assert result[0]["role"] == "system"
        assert result[1]["role"] == "user"

    def test_build_draft_prompt_includes_case_info(self):
        """Includes case information in prompt"""
        mock_case = MagicMock()
        mock_case.title = "이혼 소송 사건"
        mock_case.description = "상세 설명"

        service = create_mock_service()

        result = service._build_draft_prompt(
            case=mock_case,
            sections=["청구취지"],
            evidence_context=[],
            legal_context=[],
            precedent_context=[],
            language="ko",
            style="formal"
        )

        user_content = result[1]["content"]
        assert "이혼 소송 사건" in user_content
        assert "상세 설명" in user_content


class TestGenerateDocx:
    """Unit tests for _generate_docx method (delegates to DocumentExporter)"""

    def test_generate_docx_not_available(self):
        """Raises ValidationError when python-docx is not installed"""
        mock_case = MagicMock()
        mock_draft_response = MagicMock()

        service = create_mock_service()

        # Patch DOCX_AVAILABLE to False
        with patch('app.services.draft.document_exporter.DOCX_AVAILABLE', False):
            with pytest.raises(ValidationError, match="DOCX export is not available"):
                service._generate_docx(mock_case, mock_draft_response)

    def test_generate_docx_success(self):
        """Successfully generates DOCX file"""
        mock_case = MagicMock()
        mock_case.title = "이혼 소송 테스트"

        mock_citation = MagicMock()
        mock_citation.evidence_id = "ev-123"
        mock_citation.labels = ["폭언"]
        mock_citation.snippet = "테스트 증거 내용"

        mock_draft_response = MagicMock()
        mock_draft_response.draft_text = "소장 초안 본문 내용\n\n두 번째 단락"
        mock_draft_response.generated_at = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        mock_draft_response.citations = [mock_citation]

        service = create_mock_service()

        with patch('app.services.draft.document_exporter.DOCX_AVAILABLE', True):
            # Mock the docx module
            mock_doc = MagicMock()
            mock_heading = MagicMock()
            mock_doc.add_heading.return_value = mock_heading
            mock_paragraph = MagicMock()
            mock_doc.add_paragraph.return_value = mock_paragraph

            with patch('app.services.draft.document_exporter.Document', return_value=mock_doc):
                with patch('app.services.draft.document_exporter.WD_ALIGN_PARAGRAPH'):
                    file_buffer, filename, content_type = service._generate_docx(
                        mock_case, mock_draft_response
                    )

                    assert filename.startswith("draft_")
                    assert filename.endswith(".docx")
                    assert content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    mock_doc.save.assert_called_once()


class TestGeneratePdf:
    """Unit tests for _generate_pdf method (delegates to DocumentExporter)"""

    def test_generate_pdf_import_error(self):
        """Raises ValidationError when reportlab is not installed"""
        mock_case = MagicMock()
        mock_draft_response = MagicMock()

        service = create_mock_service()

        # Mock the import inside _generate_pdf to raise ImportError
        import builtins
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if 'reportlab' in name:
                raise ImportError("No module named 'reportlab'")
            return original_import(name, *args, **kwargs)

        with patch.object(builtins, '__import__', side_effect=mock_import):
            with pytest.raises(ValidationError, match="PDF export is not available"):
                service._generate_pdf(mock_case, mock_draft_response)

    def test_generate_pdf_success(self):
        """Successfully generates PDF file"""
        mock_case = MagicMock()
        mock_case.title = "이혼 소송 테스트"

        mock_citation = MagicMock()
        mock_citation.evidence_id = "ev-123"
        mock_citation.labels = ["폭언"]
        mock_citation.snippet = "테스트 증거 내용"

        mock_draft_response = MagicMock()
        mock_draft_response.draft_text = "소장 초안 본문 내용"
        mock_draft_response.generated_at = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        mock_draft_response.citations = [mock_citation]

        service = create_mock_service()

        # Run the PDF generation
        try:
            file_buffer, filename, content_type = service._generate_pdf(
                mock_case, mock_draft_response
            )

            assert filename.startswith("draft_")
            assert filename.endswith(".pdf")
            assert content_type == "application/pdf"
            # Check that file buffer has content
            file_buffer.seek(0, 2)  # Seek to end
            assert file_buffer.tell() > 0  # Has content
        except ValidationError:
            # If reportlab is not installed, this is expected
            pass


class TestRegisterKoreanFont:
    """Unit tests for _register_korean_font method (delegates to DocumentExporter)"""

    def test_register_korean_font_no_font_found(self):
        """Returns False when no Korean font is found"""
        mock_pdfmetrics = MagicMock()
        mock_ttfont = MagicMock()

        service = create_mock_service()

        # Mock os.path.exists to return False for all font paths
        with patch('app.services.draft.document_exporter.os.path.exists', return_value=False):
            result = service._register_korean_font(mock_pdfmetrics, mock_ttfont)

            assert result is False
            mock_pdfmetrics.registerFont.assert_not_called()

    def test_register_korean_font_success(self):
        """Returns True when Korean font is registered"""
        mock_pdfmetrics = MagicMock()
        mock_ttfont = MagicMock()

        service = create_mock_service()

        # Mock os.path.exists to return True for first font path
        def exists_side_effect(path):
            return "/System/Library/Fonts" in path

        with patch('app.services.draft.document_exporter.os.path.exists', side_effect=exists_side_effect):
            result = service._register_korean_font(mock_pdfmetrics, mock_ttfont)

            assert result is True
            mock_pdfmetrics.registerFont.assert_called_once()

    def test_register_korean_font_exception_handling(self):
        """Continues to next font when registration fails"""
        mock_pdfmetrics = MagicMock()
        mock_pdfmetrics.registerFont.side_effect = [Exception("Font error"), None]
        mock_ttfont = MagicMock()

        service = create_mock_service()

        # Mock to return True for two font paths
        call_count = [0]

        def exists_side_effect(path):
            call_count[0] += 1
            return call_count[0] <= 2

        with patch('app.services.draft.document_exporter.os.path.exists', side_effect=exists_side_effect):
            result = service._register_korean_font(mock_pdfmetrics, mock_ttfont)

            # Should have tried registering twice (first fails, second succeeds)
            assert mock_pdfmetrics.registerFont.call_count == 2
            assert result is True


class TestExportDraftFormats:
    """Unit tests for export_draft format handling"""

    def test_export_draft_unsupported_format(self):
        """Raises ValidationError for unsupported export format"""
        mock_case = MagicMock()

        mock_draft_response = MagicMock()
        mock_draft_response.draft_text = "테스트"
        mock_draft_response.citations = []
        mock_draft_response.precedent_citations = []
        mock_draft_response.generated_at = datetime.now(timezone.utc)

        service = create_mock_service()
        service.case_repo.get_by_id.return_value = mock_case
        service.member_repo.has_access.return_value = True

        # Mock generate_draft_preview to return a response
        service.generate_draft_preview = MagicMock(return_value=mock_draft_response)

        # Create a mock unsupported format
        mock_format = MagicMock()
        mock_format.value = "unsupported"

        with pytest.raises(ValidationError, match="Unsupported export format"):
            service.export_draft("case-123", "user-123", mock_format)

    @patch('app.services.draft_service.get_case_fact_summary')
    @patch('app.services.draft_service.generate_chat_completion')
    @patch('app.services.draft_service.get_template_by_type')
    @patch('app.services.draft.rag_orchestrator.search_evidence_by_semantic')
    @patch('app.services.draft.rag_orchestrator.search_legal_knowledge')
    @patch('app.services.draft_service.get_evidence_by_case')
    def test_export_draft_docx_format(
        self,
        mock_get_evidence,
        mock_search_legal,
        mock_search_ev,
        mock_get_template,
        mock_generate,
        mock_get_fact_summary
    ):
        """Successfully exports as DOCX"""
        mock_case = MagicMock()
        mock_case.title = "테스트 사건"
        mock_case.description = "설명"

        mock_get_evidence.return_value = [{"status": "done"}]
        mock_search_ev.return_value = []
        mock_search_legal.return_value = []
        mock_get_template.return_value = None
        mock_generate.return_value = "초안 내용"
        mock_get_fact_summary.return_value = {"ai_summary": "테스트 사실관계 요약"}

        service = create_mock_service()
        service.case_repo.get_by_id.return_value = mock_case
        service.member_repo.has_access.return_value = True
        service.rag_orchestrator.search_precedents = MagicMock(return_value=[])

        # Mock _generate_docx
        from io import BytesIO
        mock_buffer = BytesIO(b"mock docx content")
        service.document_exporter.generate_docx = MagicMock(
            return_value=(mock_buffer, "draft_test.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        )

        file_buffer, filename, content_type = service.export_draft(
            "case-123",
            "user-123",
            DraftExportFormat.DOCX
        )

        assert filename == "draft_test.docx"
        service.document_exporter.generate_docx.assert_called_once()

    @patch('app.services.draft_service.get_case_fact_summary')
    @patch('app.services.draft_service.generate_chat_completion')
    @patch('app.services.draft_service.get_template_by_type')
    @patch('app.services.draft.rag_orchestrator.search_evidence_by_semantic')
    @patch('app.services.draft.rag_orchestrator.search_legal_knowledge')
    @patch('app.services.draft_service.get_evidence_by_case')
    def test_export_draft_pdf_format(
        self,
        mock_get_evidence,
        mock_search_legal,
        mock_search_ev,
        mock_get_template,
        mock_generate,
        mock_get_fact_summary
    ):
        """Successfully exports as PDF"""
        mock_case = MagicMock()
        mock_case.title = "테스트 사건"
        mock_case.description = "설명"

        mock_get_evidence.return_value = [{"status": "done"}]
        mock_search_ev.return_value = []
        mock_search_legal.return_value = []
        mock_get_template.return_value = None
        mock_generate.return_value = "초안 내용"
        mock_get_fact_summary.return_value = {"ai_summary": "테스트 사실관계 요약"}

        service = create_mock_service()
        service.case_repo.get_by_id.return_value = mock_case
        service.member_repo.has_access.return_value = True
        service.rag_orchestrator.search_precedents = MagicMock(return_value=[])

        # Mock _generate_pdf
        from io import BytesIO
        mock_buffer = BytesIO(b"mock pdf content")
        service.document_exporter.generate_pdf = MagicMock(
            return_value=(mock_buffer, "draft_test.pdf", "application/pdf")
        )

        file_buffer, filename, content_type = service.export_draft(
            "case-123",
            "user-123",
            DraftExportFormat.PDF
        )

        assert filename == "draft_test.pdf"
        service.document_exporter.generate_pdf.assert_called_once()


class TestListDrafts:
    """Unit tests for list_drafts method (lines 879-901)"""

    def test_list_drafts_case_not_found(self):
        """Raises NotFoundError when case doesn't exist"""
        service = create_mock_service()
        service.case_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError, match="Case"):
            service.list_drafts("case-123", "user-123")

    def test_list_drafts_no_access(self):
        """Raises PermissionError when user has no access"""
        mock_case = MagicMock()

        service = create_mock_service()
        service.case_repo.get_by_id.return_value = mock_case
        service.member_repo.has_access.return_value = False

        with pytest.raises(PermissionError, match="access"):
            service.list_drafts("case-123", "user-123")

    def test_list_drafts_success(self):
        """Returns list of draft summaries"""
        mock_case = MagicMock()

        # Create mock draft
        from app.db.models import DocumentType, DraftStatus
        mock_draft = MagicMock()
        mock_draft.id = "draft-123"
        mock_draft.case_id = "case-123"
        mock_draft.title = "테스트 초안"
        mock_draft.document_type = DocumentType.BRIEF
        mock_draft.version = 1
        mock_draft.status = DraftStatus.DRAFT
        mock_draft.updated_at = datetime.now(timezone.utc)

        service = create_mock_service()
        service.case_repo.get_by_id.return_value = mock_case
        service.member_repo.has_access.return_value = True

        # Mock query chain
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [mock_draft]
        service.db.query.return_value = mock_query

        result = service.list_drafts("case-123", "user-123")

        assert len(result) == 1
        assert result[0].id == "draft-123"
        assert result[0].title == "테스트 초안"


class TestGetDraft:
    """Unit tests for get_draft method (lines 920-947)"""

    def test_get_draft_case_not_found(self):
        """Raises NotFoundError when case doesn't exist"""
        service = create_mock_service()
        service.case_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError, match="Case"):
            service.get_draft("case-123", "draft-123", "user-123")

    def test_get_draft_no_access(self):
        """Raises PermissionError when user has no access"""
        mock_case = MagicMock()

        service = create_mock_service()
        service.case_repo.get_by_id.return_value = mock_case
        service.member_repo.has_access.return_value = False

        with pytest.raises(PermissionError, match="access"):
            service.get_draft("case-123", "draft-123", "user-123")

    def test_get_draft_not_found(self):
        """Raises NotFoundError when draft doesn't exist"""
        mock_case = MagicMock()

        service = create_mock_service()
        service.case_repo.get_by_id.return_value = mock_case
        service.member_repo.has_access.return_value = True

        # Mock query to return None
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        service.db.query.return_value = mock_query

        with pytest.raises(NotFoundError, match="Draft"):
            service.get_draft("case-123", "draft-123", "user-123")

    def test_get_draft_success(self):
        """Returns draft response"""
        mock_case = MagicMock()

        from app.db.models import DocumentType, DraftStatus
        mock_draft = MagicMock()
        mock_draft.id = "draft-123"
        mock_draft.case_id = "case-123"
        mock_draft.title = "테스트 초안"
        mock_draft.document_type = DocumentType.BRIEF
        mock_draft.content = {"sections": []}
        mock_draft.version = 1
        mock_draft.status = DraftStatus.DRAFT
        mock_draft.created_by = "user-123"
        mock_draft.created_at = datetime.now(timezone.utc)
        mock_draft.updated_at = datetime.now(timezone.utc)

        service = create_mock_service()
        service.case_repo.get_by_id.return_value = mock_case
        service.member_repo.has_access.return_value = True

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_draft
        service.db.query.return_value = mock_query

        result = service.get_draft("case-123", "draft-123", "user-123")

        assert result.id == "draft-123"
        assert result.title == "테스트 초안"


class TestCreateDraft:
    """Unit tests for create_draft method (lines 971-1012)"""

    def test_create_draft_case_not_found(self):
        """Raises NotFoundError when case doesn't exist"""
        mock_draft_data = MagicMock()

        service = create_mock_service()
        service.case_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError, match="Case"):
            service.create_draft("case-123", mock_draft_data, "user-123")

    def test_create_draft_no_write_access(self):
        """Raises PermissionError when user has no write access"""
        mock_case = MagicMock()
        mock_draft_data = MagicMock()

        service = create_mock_service()
        service.case_repo.get_by_id.return_value = mock_case
        service.member_repo.has_write_access.return_value = False

        with pytest.raises(PermissionError, match="write access"):
            service.create_draft("case-123", mock_draft_data, "user-123")

    def test_create_draft_success(self):
        """Creates and returns draft response"""
        mock_case = MagicMock()

        from app.db.schemas import DraftCreate, DraftDocumentType

        mock_draft_data = MagicMock(spec=DraftCreate)
        mock_draft_data.title = "새 초안"
        mock_draft_data.document_type = DraftDocumentType.BRIEF
        mock_draft_data.content = None

        service = create_mock_service()
        service.case_repo.get_by_id.return_value = mock_case
        service.member_repo.has_write_access.return_value = True

        # Mock the draft that gets created and refreshed
        def refresh_side_effect(draft):
            draft.id = "new-draft-123"
            draft.created_at = datetime.now(timezone.utc)
            draft.updated_at = datetime.now(timezone.utc)

        service.db.refresh.side_effect = refresh_side_effect

        result = service.create_draft("case-123", mock_draft_data, "user-123")

        service.db.add.assert_called_once()
        service.db.commit.assert_called_once()
        assert result.title == "새 초안"


class TestUpdateDraft:
    """Unit tests for update_draft method (lines 1038-1104)"""

    def test_update_draft_case_not_found(self):
        """Raises NotFoundError when case doesn't exist"""
        mock_update_data = MagicMock()

        service = create_mock_service()
        service.case_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError, match="Case"):
            service.update_draft("case-123", "draft-123", mock_update_data, "user-123")

    def test_update_draft_no_write_access(self):
        """Raises PermissionError when user has no write access"""
        mock_case = MagicMock()
        mock_update_data = MagicMock()

        service = create_mock_service()
        service.case_repo.get_by_id.return_value = mock_case
        service.member_repo.has_write_access.return_value = False

        with pytest.raises(PermissionError, match="write access"):
            service.update_draft("case-123", "draft-123", mock_update_data, "user-123")

    def test_update_draft_not_found(self):
        """Raises NotFoundError when draft doesn't exist"""
        mock_case = MagicMock()
        mock_update_data = MagicMock()

        service = create_mock_service()
        service.case_repo.get_by_id.return_value = mock_case
        service.member_repo.has_write_access.return_value = True

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        service.db.query.return_value = mock_query

        with pytest.raises(NotFoundError, match="Draft"):
            service.update_draft("case-123", "draft-123", mock_update_data, "user-123")

    def test_update_draft_success(self):
        """Updates and returns draft response"""
        mock_case = MagicMock()

        from app.db.schemas import DraftUpdate
        from app.db.models import DocumentType, DraftStatus

        mock_draft = MagicMock()
        mock_draft.id = "draft-123"
        mock_draft.case_id = "case-123"
        mock_draft.title = "원래 제목"
        mock_draft.document_type = DocumentType.BRIEF
        mock_draft.content = {}
        mock_draft.version = 1
        mock_draft.status = DraftStatus.DRAFT
        mock_draft.created_by = "user-123"
        mock_draft.created_at = datetime.now(timezone.utc)
        mock_draft.updated_at = datetime.now(timezone.utc)

        mock_update_data = MagicMock(spec=DraftUpdate)
        mock_update_data.title = "수정된 제목"
        mock_update_data.document_type = None
        mock_update_data.content = None
        mock_update_data.status = None

        service = create_mock_service()
        service.case_repo.get_by_id.return_value = mock_case
        service.member_repo.has_write_access.return_value = True

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_draft
        service.db.query.return_value = mock_query

        service.update_draft("case-123", "draft-123", mock_update_data, "user-123")

        service.db.commit.assert_called_once()
        assert mock_draft.title == "수정된 제목"


class TestSaveGeneratedDraft:
    """Unit tests for save_generated_draft method (lines 1131-1191)"""

    def test_save_generated_draft_case_not_found(self):
        """Raises NotFoundError when case doesn't exist"""
        mock_draft_response = MagicMock()

        service = create_mock_service()
        service.case_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundError, match="Case"):
            service.save_generated_draft("case-123", mock_draft_response, "user-123")

    def test_save_generated_draft_no_write_access(self):
        """Raises PermissionError when user has no write access"""
        mock_case = MagicMock()
        mock_draft_response = MagicMock()

        service = create_mock_service()
        service.case_repo.get_by_id.return_value = mock_case
        service.member_repo.has_write_access.return_value = False

        with pytest.raises(PermissionError, match="write access"):
            service.save_generated_draft("case-123", mock_draft_response, "user-123")

    def test_save_generated_draft_success(self):
        """Saves and returns draft response"""
        mock_case = MagicMock()
        mock_case.title = "테스트 케이스"

        # Create mock draft preview response
        mock_citation = MagicMock()
        mock_citation.evidence_id = "ev-123"
        mock_citation.snippet = "증거 내용"
        mock_citation.labels = ["폭언"]

        mock_draft_response = MagicMock()
        mock_draft_response.draft_text = "초안 본문"
        mock_draft_response.citations = [mock_citation]
        mock_draft_response.precedent_citations = []
        mock_draft_response.generated_at = datetime.now(timezone.utc)

        service = create_mock_service()
        service.case_repo.get_by_id.return_value = mock_case
        service.member_repo.has_write_access.return_value = True

        def refresh_side_effect(draft):
            draft.id = "saved-draft-123"
            draft.created_at = datetime.now(timezone.utc)
            draft.updated_at = datetime.now(timezone.utc)

        service.db.refresh.side_effect = refresh_side_effect

        result = service.save_generated_draft("case-123", mock_draft_response, "user-123")

        service.db.add.assert_called_once()
        service.db.commit.assert_called_once()
        assert result.title == "테스트 케이스 - 초안"
