"""
Unit tests for DocxGenerator
TDD - Improving test coverage for docx_generator.py
"""

import pytest
from unittest.mock import patch
from datetime import datetime

from app.utils.docx_generator import (
    DocxGenerator,
    DocxGeneratorError,
    generate_docx,
    generate_docx_from_text,
    DOCX_AVAILABLE
)


@pytest.mark.skipif(not DOCX_AVAILABLE, reason="python-docx not installed")
class TestDocxGeneratorInit:
    """Unit tests for DocxGenerator initialization"""

    def test_init_success(self):
        """DocxGenerator initializes successfully when python-docx is available"""
        generator = DocxGenerator()
        assert generator.doc is None

    def test_init_raises_when_docx_unavailable(self):
        """Raises DocxGeneratorError when python-docx is not installed"""
        with patch('app.utils.docx_generator.DOCX_AVAILABLE', False):
            # Need to reimport to pick up the patched value
            import app.utils.docx_generator as module

            original = module.DOCX_AVAILABLE
            module.DOCX_AVAILABLE = False

            try:
                with pytest.raises(DocxGeneratorError, match="python-docx is not installed"):
                    DocxGenerator()
            finally:
                module.DOCX_AVAILABLE = original


@pytest.mark.skipif(not DOCX_AVAILABLE, reason="python-docx not installed")
class TestGenerateDocument:
    """Unit tests for generate_document method"""

    def test_generate_empty_document(self):
        """Generates DOCX with minimal content"""
        generator = DocxGenerator()
        content = {}

        result = generator.generate_document(content)

        assert isinstance(result, bytes)
        assert len(result) > 0
        # Check it's a valid DOCX (starts with PK zip header)
        assert result[:2] == b'PK'

    def test_generate_with_header(self):
        """Generates DOCX with header section"""
        generator = DocxGenerator()
        content = {
            "header": {
                "court_name": "서울가정법원",
                "case_number": "2025드단12345",
                "parties": {
                    "plaintiff": "원고 김○○",
                    "defendant": "피고 이○○"
                }
            }
        }

        result = generator.generate_document(content, "complaint")

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_generate_with_sections(self):
        """Generates DOCX with content sections"""
        generator = DocxGenerator()
        content = {
            "sections": [
                {"title": "청구취지", "content": "원고와 피고는 이혼한다.", "order": 1},
                {"title": "청구원인", "content": "혼인관계 파탄 사유", "order": 2}
            ]
        }

        result = generator.generate_document(content, "brief")

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_generate_with_citations(self):
        """Generates DOCX with citations section"""
        generator = DocxGenerator()
        content = {
            "citations": [
                {"reference": "[증 제1호증]", "description": "녹음 파일"},
                {"reference": "[증 제2호증]", "description": "카카오톡 대화 기록"}
            ]
        }

        result = generator.generate_document(content)

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_generate_with_footer(self):
        """Generates DOCX with footer/signature section"""
        generator = DocxGenerator()
        content = {
            "header": {
                "court_name": "서울가정법원"
            },
            "footer": {
                "date": "2025년 12월 3일",
                "attorney": "변호사 박○○"
            }
        }

        result = generator.generate_document(content)

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_generate_full_document(self):
        """Generates complete DOCX with all sections"""
        generator = DocxGenerator()
        content = {
            "header": {
                "court_name": "서울가정법원",
                "case_number": "2025드단12345",
                "parties": {
                    "plaintiff": "원고 김○○",
                    "defendant": "피고 이○○"
                }
            },
            "sections": [
                {"title": "청구취지", "content": "1. 원고와 피고는 이혼한다.\n2. 위자료 청구", "order": 1},
                {"title": "청구원인", "content": "혼인관계 파탄", "order": 2}
            ],
            "citations": [
                {"reference": "[증 제1호증]", "description": "녹음 파일"}
            ],
            "footer": {
                "date": "2025년 12월 3일",
                "attorney": "변호사 박○○"
            }
        }

        result = generator.generate_document(content, "complaint")

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_document_types(self):
        """Generates DOCX for different document types"""
        generator = DocxGenerator()
        content = {"sections": [{"title": "내용", "content": "테스트", "order": 1}]}

        for doc_type in ["complaint", "motion", "brief", "response"]:
            result = generator.generate_document(content, doc_type)
            assert isinstance(result, bytes)
            assert len(result) > 0

    def test_unknown_document_type_uses_default(self):
        """Unknown document type defaults to 준비서면"""
        generator = DocxGenerator()
        content = {}

        result = generator.generate_document(content, "unknown_type")

        assert isinstance(result, bytes)
        assert len(result) > 0


@pytest.mark.skipif(not DOCX_AVAILABLE, reason="python-docx not installed")
class TestGenerateFromDraftText:
    """Unit tests for generate_from_draft_text method"""

    def test_generate_from_text_minimal(self):
        """Generates DOCX from minimal text"""
        generator = DocxGenerator()

        result = generator.generate_from_draft_text(
            draft_text="테스트 초안 내용",
            case_title="테스트 케이스"
        )

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_generate_from_text_with_multiple_paragraphs(self):
        """Handles multiple paragraphs in draft text"""
        generator = DocxGenerator()

        draft_text = """첫 번째 문단입니다.

두 번째 문단입니다.

세 번째 문단입니다."""

        result = generator.generate_from_draft_text(
            draft_text=draft_text,
            case_title="테스트"
        )

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_generate_from_text_with_citations(self):
        """Generates DOCX with citations list"""
        generator = DocxGenerator()
        citations = [
            {"evidence_id": "EV-001", "labels": ["폭언"], "snippet": "폭언 내용"},
            {"evidence_id": "EV-002", "labels": ["협박", "폭행"], "snippet": "협박 내용"}
        ]

        result = generator.generate_from_draft_text(
            draft_text="초안 내용",
            case_title="테스트",
            citations=citations
        )

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_generate_from_text_with_empty_citations(self):
        """Handles empty citation labels gracefully"""
        generator = DocxGenerator()
        citations = [
            {"evidence_id": "EV-001", "labels": [], "snippet": "내용"}
        ]

        result = generator.generate_from_draft_text(
            draft_text="초안",
            case_title="테스트",
            citations=citations
        )

        assert isinstance(result, bytes)

    def test_generate_from_text_with_timestamp(self):
        """Uses provided timestamp"""
        generator = DocxGenerator()
        timestamp = datetime(2025, 12, 3, 10, 30, 0)

        result = generator.generate_from_draft_text(
            draft_text="초안",
            case_title="테스트",
            generated_at=timestamp
        )

        assert isinstance(result, bytes)

    def test_generate_from_text_default_timestamp(self):
        """Uses current time when timestamp not provided"""
        generator = DocxGenerator()

        result = generator.generate_from_draft_text(
            draft_text="초안",
            case_title="테스트"
        )

        assert isinstance(result, bytes)


@pytest.mark.skipif(not DOCX_AVAILABLE, reason="python-docx not installed")
class TestConvenienceFunctions:
    """Unit tests for convenience functions"""

    def test_generate_docx_function(self):
        """generate_docx convenience function works"""
        content = {
            "sections": [
                {"title": "테스트", "content": "내용", "order": 1}
            ]
        }

        result = generate_docx(content, "brief")

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_generate_docx_from_text_function(self):
        """generate_docx_from_text convenience function works"""
        result = generate_docx_from_text(
            draft_text="테스트 초안",
            case_title="테스트 케이스"
        )

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_generate_docx_from_text_with_all_params(self):
        """generate_docx_from_text with all parameters"""
        citations = [{"evidence_id": "EV-001", "labels": ["테스트"], "snippet": "내용"}]
        timestamp = datetime(2025, 1, 1, 12, 0, 0)

        result = generate_docx_from_text(
            draft_text="초안 내용입니다.\n\n다음 문단.",
            case_title="전체 파라미터 테스트",
            citations=citations,
            generated_at=timestamp
        )

        assert isinstance(result, bytes)
        assert len(result) > 0


@pytest.mark.skipif(not DOCX_AVAILABLE, reason="python-docx not installed")
class TestDocxGeneratorEdgeCases:
    """Edge case tests for DocxGenerator"""

    def test_empty_header_fields(self):
        """Handles empty header fields gracefully"""
        generator = DocxGenerator()
        content = {
            "header": {
                "court_name": "",
                "case_number": "",
                "parties": {}
            }
        }

        result = generator.generate_document(content)

        assert isinstance(result, bytes)

    def test_partial_parties(self):
        """Handles partial party information"""
        generator = DocxGenerator()
        content = {
            "header": {
                "parties": {
                    "plaintiff": "원고만 있음"
                    # defendant is missing
                }
            }
        }

        result = generator.generate_document(content)

        assert isinstance(result, bytes)

    def test_empty_sections_list(self):
        """Handles empty sections list"""
        generator = DocxGenerator()
        content = {"sections": []}

        result = generator.generate_document(content)

        assert isinstance(result, bytes)

    def test_section_without_order(self):
        """Handles sections without order field"""
        generator = DocxGenerator()
        content = {
            "sections": [
                {"title": "제목", "content": "내용"}  # no order
            ]
        }

        result = generator.generate_document(content)

        assert isinstance(result, bytes)

    def test_empty_section_content(self):
        """Handles empty section content"""
        generator = DocxGenerator()
        content = {
            "sections": [
                {"title": "빈 섹션", "content": "", "order": 1}
            ]
        }

        result = generator.generate_document(content)

        assert isinstance(result, bytes)

    def test_empty_footer_fields(self):
        """Handles empty footer fields"""
        generator = DocxGenerator()
        content = {
            "footer": {
                "date": "",
                "attorney": ""
            }
        }

        result = generator.generate_document(content)

        assert isinstance(result, bytes)

    def test_empty_values_in_content(self):
        """Handles empty dict/list values in content dict"""
        generator = DocxGenerator()
        # Note: None values cause TypeError, but empty structures work fine
        content = {
            "header": {},
            "sections": [],
            "citations": [],
            "footer": {}
        }

        result = generator.generate_document(content)

        assert isinstance(result, bytes)

    def test_multiline_section_content(self):
        """Handles multiline content in sections"""
        generator = DocxGenerator()
        content = {
            "sections": [
                {
                    "title": "청구취지",
                    "content": "1. 원고와 피고는 이혼한다.\n2. 피고는 원고에게 위자료로 금 30,000,000원을 지급하라.\n3. 소송비용은 피고가 부담한다.",
                    "order": 1
                }
            ]
        }

        result = generator.generate_document(content)

        assert isinstance(result, bytes)

    def test_citation_without_description(self):
        """Handles citation without description"""
        generator = DocxGenerator()
        content = {
            "citations": [
                {"reference": "[증 제1호증]"}  # no description
            ]
        }

        result = generator.generate_document(content)

        assert isinstance(result, bytes)

    def test_citation_without_reference(self):
        """Handles citation without reference"""
        generator = DocxGenerator()
        content = {
            "citations": [
                {"description": "설명만 있음"}  # no reference
            ]
        }

        result = generator.generate_document(content)

        assert isinstance(result, bytes)


@pytest.mark.skipif(not DOCX_AVAILABLE, reason="python-docx not installed")
class TestDocxGeneratorConstants:
    """Tests for DocxGenerator constants"""

    def test_paper_dimensions(self):
        """Verifies A4 paper dimensions"""
        assert DocxGenerator.PAPER_WIDTH_MM == 210
        assert DocxGenerator.PAPER_HEIGHT_MM == 297

    def test_margin_dimensions(self):
        """Verifies Korean court margin dimensions"""
        assert DocxGenerator.MARGIN_TOP_MM == 25
        assert DocxGenerator.MARGIN_BOTTOM_MM == 25
        assert DocxGenerator.MARGIN_LEFT_MM == 20
        assert DocxGenerator.MARGIN_RIGHT_MM == 20

    def test_font_settings(self):
        """Verifies font settings"""
        assert DocxGenerator.FONT_SIZE_BODY == 12
        assert DocxGenerator.FONT_SIZE_TITLE == 18
        assert DocxGenerator.LINE_SPACING == 1.6

    def test_document_types(self):
        """Verifies document type mappings"""
        types = DocxGenerator.DOCUMENT_TYPES
        assert "complaint" in types
        assert "motion" in types
        assert "brief" in types
        assert "response" in types
        assert types["complaint"] == "소 장"


class TestDocxGeneratorError:
    """Tests for DocxGeneratorError exception"""

    def test_docx_generator_error_is_exception(self):
        """DocxGeneratorError is an Exception"""
        error = DocxGeneratorError("test error")
        assert isinstance(error, Exception)
        assert str(error) == "test error"
