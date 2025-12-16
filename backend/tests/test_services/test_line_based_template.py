"""
TDD Tests for Line-Based Template Functionality
Tests are written FIRST, then implementation follows.

라인별 JSON 템플릿을 사용한 초안 생성 기능 테스트
"""

import pytest
import json
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

# These imports will fail until implementation is done
# This is expected in TDD - tests first, then implementation


class TestLineBasedTemplateSchema:
    """Tests for line-based template JSON schema validation"""

    def test_template_has_required_fields(self):
        """Template JSON must have template_type, version, and lines"""
        # Sample template structure
        template = {
            "template_type": "이혼소송청구",
            "version": "2.0.0",
            "lines": []
        }

        assert "template_type" in template
        assert "version" in template
        assert "lines" in template

    def test_line_structure(self):
        """Each line must have line number, text, and optional format"""
        line = {
            "line": 1,
            "text": "이 혼 소 송 청 구",
            "section": "header",
            "format": {
                "align": "center",
                "bold": True,
                "font_size": 16
            }
        }

        assert "line" in line
        assert "text" in line
        assert isinstance(line.get("format", {}), dict)

    def test_placeholder_line_structure(self):
        """Placeholder lines must have is_placeholder and placeholder_key"""
        placeholder_line = {
            "line": 3,
            "text": "{{원고이름}}",
            "section": "parties",
            "is_placeholder": True,
            "placeholder_key": "plaintiff_name"
        }

        assert placeholder_line["is_placeholder"] is True
        assert "placeholder_key" in placeholder_line
        assert "{{" in placeholder_line["text"] and "}}" in placeholder_line["text"]

    def test_conditional_line_structure(self):
        """Conditional lines must have condition field"""
        conditional_line = {
            "line": 20,
            "text": "{{친권자지정}}, {{양육자지정}} 내용",
            "section": "claims",
            "is_placeholder": True,
            "condition": "has_children"
        }

        assert "condition" in conditional_line
        assert conditional_line["condition"] == "has_children"


class TestLoadLineBasedTemplate:
    """Tests for loading line-based template from Qdrant"""

    @patch('app.services.draft_service.get_template_by_type')
    def test_load_template_success(self, mock_get_template):
        """Successfully loads line-based template from Qdrant"""
        from app.services.draft_service import DraftService

        mock_template = {
            "template_type": "이혼소송청구",
            "version": "2.0.0",
            "lines": [
                {"line": 1, "text": "이 혼 소 송 청 구", "format": {"align": "center"}}
            ]
        }
        mock_get_template.return_value = mock_template

        mock_db = MagicMock()
        with patch.object(DraftService, '__init__', lambda x, y: None):
            service = DraftService(mock_db)

            template = service.load_line_based_template("이혼소장")

            assert template is not None
            assert template["template_type"] == "이혼소송청구"
            assert len(template["lines"]) > 0

    @patch('app.services.draft_service.get_template_by_type')
    def test_load_template_not_found(self, mock_get_template):
        """Raises error when template not found"""
        from app.services.draft_service import DraftService
        from app.middleware import NotFoundError

        mock_get_template.return_value = None

        mock_db = MagicMock()
        with patch.object(DraftService, '__init__', lambda x, y: None):
            service = DraftService(mock_db)

            with pytest.raises(NotFoundError):
                service.load_line_based_template("존재하지않는템플릿")


class TestFillPlaceholders:
    """Tests for filling placeholders in line-based template"""

    def test_fill_single_placeholder(self):
        """Fills single placeholder with case data"""
        from app.services.draft_service import DraftService

        template_lines = [
            {"line": 1, "text": "{{원고이름}}", "is_placeholder": True, "placeholder_key": "plaintiff_name"}
        ]
        case_data = {
            "plaintiff_name": "김영희"
        }

        mock_db = MagicMock()
        with patch.object(DraftService, '__init__', lambda x, y: None):
            service = DraftService(mock_db)

            filled_lines = service.fill_placeholders(template_lines, case_data)

            assert filled_lines[0]["text"] == "김영희"

    def test_fill_multiple_placeholders_in_line(self):
        """Fills multiple placeholders in single line"""
        from app.services.draft_service import DraftService

        template_lines = [
            {"line": 1, "text": "원고 {{원고이름}} ({{원고주민번호}})", "is_placeholder": True}
        ]
        case_data = {
            "원고이름": "김영희",
            "원고주민번호": "800101-2******"
        }

        mock_db = MagicMock()
        with patch.object(DraftService, '__init__', lambda x, y: None):
            service = DraftService(mock_db)

            filled_lines = service.fill_placeholders(template_lines, case_data)

            assert "김영희" in filled_lines[0]["text"]
            assert "800101-2******" in filled_lines[0]["text"]

    def test_preserve_non_placeholder_lines(self):
        """Non-placeholder lines remain unchanged"""
        from app.services.draft_service import DraftService

        template_lines = [
            {"line": 1, "text": "이 혼 소 송 청 구", "is_placeholder": False},
            {"line": 2, "text": "{{원고이름}}", "is_placeholder": True, "placeholder_key": "plaintiff_name"}
        ]
        case_data = {"plaintiff_name": "김영희"}

        mock_db = MagicMock()
        with patch.object(DraftService, '__init__', lambda x, y: None):
            service = DraftService(mock_db)

            filled_lines = service.fill_placeholders(template_lines, case_data)

            assert filled_lines[0]["text"] == "이 혼 소 송 청 구"
            assert filled_lines[1]["text"] == "김영희"

    def test_missing_placeholder_data_uses_empty(self):
        """Missing placeholder data results in empty string or placeholder text"""
        from app.services.draft_service import DraftService

        template_lines = [
            {"line": 1, "text": "{{원고이름}}", "is_placeholder": True, "placeholder_key": "plaintiff_name"}
        ]
        case_data = {}  # No data provided

        mock_db = MagicMock()
        with patch.object(DraftService, '__init__', lambda x, y: None):
            service = DraftService(mock_db)

            filled_lines = service.fill_placeholders(template_lines, case_data)

            # Should either be empty or keep placeholder
            assert filled_lines[0]["text"] in ["", "{{원고이름}}", "[미입력]"]


class TestConditionalLines:
    """Tests for handling conditional lines based on case type"""

    def test_include_line_when_condition_met(self):
        """Includes conditional line when condition is met"""
        from app.services.draft_service import DraftService

        template_lines = [
            {"line": 1, "text": "이 혼 소 송 청 구"},
            {"line": 2, "text": "친권자 지정: {{친권자지정}}", "condition": "has_children", "is_placeholder": True}
        ]
        case_conditions = {
            "has_children": True
        }

        mock_db = MagicMock()
        with patch.object(DraftService, '__init__', lambda x, y: None):
            service = DraftService(mock_db)

            filtered_lines = service.filter_conditional_lines(template_lines, case_conditions)

            assert len(filtered_lines) == 2

    def test_exclude_line_when_condition_not_met(self):
        """Excludes conditional line when condition is not met"""
        from app.services.draft_service import DraftService

        template_lines = [
            {"line": 1, "text": "이 혼 소 송 청 구"},
            {"line": 2, "text": "친권자 지정: {{친권자지정}}", "condition": "has_children", "is_placeholder": True}
        ]
        case_conditions = {
            "has_children": False
        }

        mock_db = MagicMock()
        with patch.object(DraftService, '__init__', lambda x, y: None):
            service = DraftService(mock_db)

            filtered_lines = service.filter_conditional_lines(template_lines, case_conditions)

            assert len(filtered_lines) == 1
            assert filtered_lines[0]["text"] == "이 혼 소 송 청 구"

    def test_include_unconditional_lines(self):
        """Lines without condition are always included"""
        from app.services.draft_service import DraftService

        template_lines = [
            {"line": 1, "text": "이 혼 소 송 청 구"},
            {"line": 2, "text": "원고: {{원고이름}}", "is_placeholder": True},
            {"line": 3, "text": "위자료: {{위자료금액}}", "condition": "has_alimony", "is_placeholder": True}
        ]
        case_conditions = {
            "has_alimony": False
        }

        mock_db = MagicMock()
        with patch.object(DraftService, '__init__', lambda x, y: None):
            service = DraftService(mock_db)

            filtered_lines = service.filter_conditional_lines(template_lines, case_conditions)

            # Lines 1 and 2 have no condition, so they're included
            # Line 3 has condition=has_alimony which is False, so excluded
            assert len(filtered_lines) == 2


class TestAIGeneratedContent:
    """Tests for AI-generated content in placeholders"""

    @patch('app.services.draft_service.generate_chat_completion')
    def test_generate_ai_content_for_placeholder(self, mock_gpt):
        """Generates AI content for ai_generated placeholders"""
        from app.services.draft_service import DraftService

        mock_gpt.return_value = "피고는 원고에게 지속적인 폭언을 하였으며..."

        template_lines = [
            {"line": 1, "text": "{{청구원인_내용}}", "is_placeholder": True,
             "placeholder_key": "grounds_content", "ai_generated": True}
        ]
        evidence_context = [
            {"content": "피고가 욕설을 했다", "labels": ["폭언"]}
        ]

        mock_db = MagicMock()
        with patch.object(DraftService, '__init__', lambda x, y: None):
            service = DraftService(mock_db)

            filled_lines = service.fill_ai_generated_content(
                template_lines,
                evidence_context,
                case_id="test_case"
            )

            assert "피고는" in filled_lines[0]["text"]
            mock_gpt.assert_called_once()

    def test_skip_non_ai_generated_placeholders(self):
        """Skips placeholders not marked as ai_generated"""
        from app.services.draft_service import DraftService

        template_lines = [
            {"line": 1, "text": "{{원고이름}}", "is_placeholder": True, "placeholder_key": "plaintiff_name"},
            {"line": 2, "text": "{{청구원인_내용}}", "is_placeholder": True, "ai_generated": True}
        ]

        mock_db = MagicMock()
        with patch.object(DraftService, '__init__', lambda x, y: None):
            service = DraftService(mock_db)

            # Line 1 should not trigger AI generation
            # Only line 2 should
            with patch('app.services.draft_service.generate_chat_completion') as mock_gpt:
                mock_gpt.return_value = "AI 생성 내용"

                service.fill_ai_generated_content(template_lines, [], case_id="test")

                # Should only be called once (for ai_generated=True line)
                assert mock_gpt.call_count == 1


class TestRenderLinesToText:
    """Tests for rendering line-based JSON to formatted text"""

    def test_render_basic_text(self):
        """Renders basic text lines"""
        from app.services.draft_service import DraftService

        lines = [
            {"line": 1, "text": "이 혼 소 송 청 구"},
            {"line": 2, "text": ""},
            {"line": 3, "text": "원고  김영희"}
        ]

        mock_db = MagicMock()
        with patch.object(DraftService, '__init__', lambda x, y: None):
            service = DraftService(mock_db)

            result = service.render_lines_to_text(lines)

            assert "이 혼 소 송 청 구" in result
            assert "원고  김영희" in result

    def test_render_with_indent(self):
        """Renders text with proper indentation"""
        from app.services.draft_service import DraftService

        lines = [
            {"line": 1, "text": "원고  김영희", "format": {"indent": 0}},
            {"line": 2, "text": "주소: 서울시 강남구", "format": {"indent": 6}}
        ]

        mock_db = MagicMock()
        with patch.object(DraftService, '__init__', lambda x, y: None):
            service = DraftService(mock_db)

            result = service.render_lines_to_text(lines)

            lines_output = result.split('\n')
            # Second line should have more leading whitespace
            assert lines_output[1].startswith("      ")  # 6 spaces

    def test_render_empty_lines_for_spacing(self):
        """Renders empty lines for vertical spacing"""
        from app.services.draft_service import DraftService

        lines = [
            {"line": 1, "text": "제목"},
            {"line": 2, "text": "", "format": {"spacing_after": 2}},
            {"line": 3, "text": "본문"}
        ]

        mock_db = MagicMock()
        with patch.object(DraftService, '__init__', lambda x, y: None):
            service = DraftService(mock_db)

            result = service.render_lines_to_text(lines)

            # Should have blank lines between title and body
            assert "\n\n" in result


class TestGenerateLineBasedDraft:
    """Integration tests for line-based draft generation"""

    @patch('app.services.draft_service.generate_chat_completion')
    @patch('app.services.draft_service.search_evidence_by_semantic')
    @patch('app.services.draft_service.get_evidence_by_case')
    @patch('app.services.draft_service.get_template_by_type')
    def test_generate_full_draft_from_template(
        self,
        mock_get_template,
        mock_get_evidence,
        mock_rag_search,
        mock_gpt
    ):
        """Full integration test: template -> placeholders -> AI content -> text"""
        from app.services.draft_service import DraftService
        from app.db.schemas import DraftPreviewRequest

        # Setup mocks
        mock_get_template.return_value = {
            "template_type": "이혼소송청구",
            "version": "2.0.0",
            "lines": [
                {"line": 1, "text": "이 혼 소 송 청 구", "format": {"align": "center", "bold": True}},
                {"line": 2, "text": ""},
                {"line": 3, "text": "원고  {{원고이름}}", "is_placeholder": True},
                {"line": 4, "text": "청 구 취 지", "format": {"align": "center"}},
                {"line": 5, "text": "{{청구취지_내용}}", "is_placeholder": True, "ai_generated": True}
            ]
        }
        mock_get_evidence.return_value = [{"id": "ev_001", "status": "done"}]
        mock_rag_search.return_value = [{"content": "증거 내용", "labels": ["폭언"]}]
        mock_gpt.return_value = "피고는 원고와 이혼하라."

        mock_db = MagicMock()
        mock_case = MagicMock()
        mock_case.title = "이혼 사건"
        mock_case.description = "테스트"

        with patch.object(DraftService, '__init__', lambda x, y: None):
            service = DraftService(mock_db)
            service.db = mock_db
            service.case_repo = MagicMock()
            service.member_repo = MagicMock()
            service.case_repo.get_by_id.return_value = mock_case
            service.member_repo.has_access.return_value = True

            # Provide case data
            case_data = {
                "원고이름": "김영희"
            }

            result = service.generate_line_based_draft(
                case_id="case_123",
                user_id="user_456",
                case_data=case_data,
                template_type="이혼소장"
            )

            # Verify result structure
            assert result is not None
            assert "lines" in result or hasattr(result, 'draft_text')


class TestLineBasedDocxExport:
    """Tests for exporting line-based draft to DOCX"""

    def test_export_lines_to_docx(self):
        """Exports line-based JSON directly to DOCX with formatting"""
        from app.services.draft_service import DraftService

        lines = [
            {"line": 1, "text": "이 혼 소 송 청 구", "format": {"align": "center", "bold": True, "font_size": 16}},
            {"line": 2, "text": ""},
            {"line": 3, "text": "원고  김영희", "format": {"indent": 0}},
            {"line": 4, "text": "주소: 서울시 강남구", "format": {"indent": 6}}
        ]

        mock_db = MagicMock()
        mock_case = MagicMock()
        mock_case.title = "테스트 사건"

        with patch.object(DraftService, '__init__', lambda x, y: None):
            service = DraftService(mock_db)

            with patch('app.services.draft_service.DOCX_AVAILABLE', True):
                mock_doc = MagicMock()
                with patch('app.services.draft_service.Document', return_value=mock_doc):
                    file_buffer, filename, content_type = service.generate_docx_from_lines(
                        mock_case, lines
                    )

                    assert filename.endswith(".docx")
                    # Verify Document methods were called for each line
                    assert mock_doc.add_paragraph.called


class TestLineBasedPdfExport:
    """Tests for exporting line-based draft to PDF"""

    def test_export_lines_to_pdf(self):
        """Exports line-based JSON directly to PDF with formatting"""
        from app.services.draft_service import DraftService

        lines = [
            {"line": 1, "text": "이 혼 소 송 청 구", "format": {"align": "center", "bold": True}},
            {"line": 2, "text": "원고  김영희"}
        ]

        mock_db = MagicMock()
        mock_case = MagicMock()
        mock_case.title = "테스트 사건"

        with patch.object(DraftService, '__init__', lambda x, y: None):
            service = DraftService(mock_db)
            service._register_korean_font = MagicMock(return_value=False)

            try:
                file_buffer, filename, content_type = service.generate_pdf_from_lines(
                    mock_case, lines
                )

                assert filename.endswith(".pdf")
                assert content_type == "application/pdf"
            except Exception as e:
                # reportlab may not be installed
                if "PDF export is not available" not in str(e):
                    raise
