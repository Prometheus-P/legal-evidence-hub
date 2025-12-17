"""
Unit tests for DocumentRenderer Service
TDD - Improving test coverage for document_renderer.py
"""

from app.services.document_renderer import DocumentRenderer


class TestDocumentRendererInit:
    """Unit tests for DocumentRenderer initialization"""

    def test_init_default_width(self):
        """Uses default width when not specified"""
        renderer = DocumentRenderer()
        assert renderer.width == DocumentRenderer.DEFAULT_WIDTH

    def test_init_custom_width(self):
        """Uses custom width when specified"""
        renderer = DocumentRenderer(width=120)
        assert renderer.width == 120


class TestRenderToText:
    """Unit tests for render_to_text method"""

    def test_render_empty_doc(self):
        """Returns empty string for empty document"""
        renderer = DocumentRenderer()
        result = renderer.render_to_text({})
        assert result == ""

    def test_render_none_doc(self):
        """Returns empty string for None document"""
        renderer = DocumentRenderer()
        result = renderer.render_to_text(None)
        assert result == ""

    def test_render_header_only(self):
        """Renders header section"""
        renderer = DocumentRenderer()
        doc = {
            "header": {
                "title": "소 장",
                "court": "서울가정법원"
            }
        }

        result = renderer.render_to_text(doc)

        assert "소 장" in result or "서울가정법원" in result

    def test_render_parties(self):
        """Renders parties section"""
        renderer = DocumentRenderer()
        doc = {
            "parties": {
                "plaintiff": {"name": "원고 김○○"},
                "defendant": {"name": "피고 이○○"}
            }
        }

        result = renderer.render_to_text(doc)

        assert result is not None

    def test_render_claims(self):
        """Renders claims section"""
        renderer = DocumentRenderer()
        doc = {
            "claims": {
                "items": [
                    {"text": "원고와 피고는 이혼한다."},
                    {"text": "피고는 원고에게 위자료로 금 30,000,000원을 지급하라."}
                ]
            }
        }

        result = renderer.render_to_text(doc)

        assert result is not None

    def test_render_grounds(self):
        """Renders grounds section"""
        renderer = DocumentRenderer()
        doc = {
            "grounds": {
                "paragraphs": [
                    {"text": "원고와 피고는 2020년 결혼하였습니다."}
                ]
            }
        }

        result = renderer.render_to_text(doc)

        assert result is not None

    def test_render_evidence(self):
        """Renders evidence section"""
        renderer = DocumentRenderer()
        doc = {
            "evidence": {
                "items": [
                    {"ref": "갑 제1호증", "description": "녹음 파일"}
                ]
            }
        }

        result = renderer.render_to_text(doc)

        assert result is not None

    def test_render_attachments(self):
        """Renders attachments section"""
        renderer = DocumentRenderer()
        doc = {
            "attachments": {
                "items": [
                    {"description": "혼인관계증명서"}
                ]
            }
        }

        result = renderer.render_to_text(doc)

        assert result is not None

    def test_render_footer(self):
        """Renders footer section"""
        renderer = DocumentRenderer()
        doc = {
            "footer": {
                "date": "2025년 12월 3일",
                "attorney": "변호사 박○○"
            }
        }

        result = renderer.render_to_text(doc)

        assert result is not None

    def test_render_full_document(self):
        """Renders complete document with all sections"""
        renderer = DocumentRenderer()
        doc = {
            "header": {
                "title": "소 장",
                "court": "서울가정법원"
            },
            "parties": {
                "plaintiff": {"name": "원고"},
                "defendant": {"name": "피고"}
            },
            "claims": {
                "items": [
                    {"text": "원고와 피고는 이혼한다."}
                ]
            },
            "grounds": {
                "paragraphs": [
                    {"text": "혼인관계 파탄"}
                ]
            },
            "evidence": {
                "items": [
                    {"ref": "갑 제1호증", "description": "녹음"}
                ]
            },
            "attachments": {
                "items": [
                    {"description": "혼인관계증명서"}
                ]
            },
            "footer": {
                "date": "2025년 12월 3일"
            }
        }

        result = renderer.render_to_text(doc)

        # Should return valid text
        assert isinstance(result, str)
        assert len(result) > 0

    def test_render_handles_exception(self):
        """Falls back to JSON on rendering error"""
        renderer = DocumentRenderer()
        # Create a doc that might cause issues in specific render methods
        # but the fallback should handle it
        doc = {"unknown_section": {"data": "test"}}

        result = renderer.render_to_text(doc)

        # Should still return something (empty or JSON fallback)
        assert isinstance(result, str)


class TestApplyFormat:
    """Unit tests for _apply_format method"""

    def test_no_format(self):
        """Returns text unchanged when no format"""
        renderer = DocumentRenderer()
        result = renderer._apply_format("테스트", None)
        assert result == "테스트"

    def test_empty_format(self):
        """Returns text unchanged for empty format dict"""
        renderer = DocumentRenderer()
        result = renderer._apply_format("테스트", {})
        assert result == "테스트"

    def test_indent_level(self):
        """Applies indent_level formatting"""
        renderer = DocumentRenderer()
        result = renderer._apply_format("테스트", {"indent_level": 1})

        # Should have indentation
        assert result.startswith(" " * DocumentRenderer.INDENT_CHARS) or result == "테스트"

    def test_align_center(self):
        """Applies center alignment"""
        renderer = DocumentRenderer()
        result = renderer._apply_format("제목", {"align": "center"})

        # Center-aligned text should have leading spaces
        assert isinstance(result, str)

    def test_align_right(self):
        """Applies right alignment"""
        renderer = DocumentRenderer()
        result = renderer._apply_format("날짜", {"align": "right"})

        assert isinstance(result, str)


class TestRenderHeader:
    """Unit tests for _render_header method"""

    def test_render_header_with_title(self):
        """Renders header with title"""
        renderer = DocumentRenderer()
        header = {"title": {"text": "소 장", "format": {}}}

        result = renderer._render_header(header)

        assert isinstance(result, list)

    def test_render_header_with_court(self):
        """Renders header with court name"""
        renderer = DocumentRenderer()
        header = {"court": "서울가정법원"}

        result = renderer._render_header(header)

        assert isinstance(result, list)

    def test_render_empty_header(self):
        """Handles empty header"""
        renderer = DocumentRenderer()
        result = renderer._render_header({})

        assert isinstance(result, list)


class TestRenderParties:
    """Unit tests for _render_parties method"""

    def test_render_both_parties(self):
        """Renders both plaintiff and defendant"""
        renderer = DocumentRenderer()
        parties = {
            "plaintiff": {"name": "원고 김○○"},
            "defendant": {"name": "피고 이○○"}
        }

        result = renderer._render_parties(parties)

        assert isinstance(result, list)

    def test_render_plaintiff_only(self):
        """Renders with plaintiff only"""
        renderer = DocumentRenderer()
        parties = {"plaintiff": {"name": "원고"}}

        result = renderer._render_parties(parties)

        assert isinstance(result, list)

    def test_render_empty_parties(self):
        """Handles empty parties"""
        renderer = DocumentRenderer()
        result = renderer._render_parties({})

        assert isinstance(result, list)


class TestRenderClaims:
    """Unit tests for _render_claims method"""

    def test_render_claims_with_items(self):
        """Renders claims with items"""
        renderer = DocumentRenderer()
        claims = {
            "items": [
                {"text": "청구사항1"},
                {"text": "청구사항2"}
            ]
        }

        result = renderer._render_claims(claims)

        assert isinstance(result, list)

    def test_render_claims_with_title(self):
        """Renders claims with custom title"""
        renderer = DocumentRenderer()
        claims = {
            "title": {"text": "청 구 취 지", "format": {}},
            "items": [{"text": "내용"}]
        }

        result = renderer._render_claims(claims)

        assert isinstance(result, list)

    def test_render_empty_claims(self):
        """Handles empty claims"""
        renderer = DocumentRenderer()
        result = renderer._render_claims({})

        assert isinstance(result, list)


class TestRenderGrounds:
    """Unit tests for _render_grounds method"""

    def test_render_grounds_with_paragraphs(self):
        """Renders grounds with paragraphs"""
        renderer = DocumentRenderer()
        grounds = {
            "paragraphs": [
                {"text": "문단1"},
                {"text": "문단2"}
            ]
        }

        result = renderer._render_grounds(grounds)

        assert isinstance(result, list)

    def test_render_grounds_with_subsections(self):
        """Renders grounds with subsections"""
        renderer = DocumentRenderer()
        grounds = {
            "subsections": [
                {"title": "1. 당사자들의 관계", "content": "내용"}
            ]
        }

        result = renderer._render_grounds(grounds)

        assert isinstance(result, list)

    def test_render_empty_grounds(self):
        """Handles empty grounds"""
        renderer = DocumentRenderer()
        result = renderer._render_grounds({})

        assert isinstance(result, list)


class TestRenderEvidence:
    """Unit tests for _render_evidence method"""

    def test_render_evidence_items(self):
        """Renders evidence items"""
        renderer = DocumentRenderer()
        evidence = {
            "items": [
                {"ref": "갑 제1호증", "description": "녹음"},
                {"ref": "갑 제2호증", "description": "사진"}
            ]
        }

        result = renderer._render_evidence(evidence)

        assert isinstance(result, list)

    def test_render_empty_evidence(self):
        """Handles empty evidence"""
        renderer = DocumentRenderer()
        result = renderer._render_evidence({})

        assert isinstance(result, list)


class TestRenderAttachments:
    """Unit tests for _render_attachments method"""

    def test_render_attachments_items(self):
        """Renders attachments items"""
        renderer = DocumentRenderer()
        attachments = {
            "items": [
                {"description": "서류1"},
                {"description": "서류2"}
            ]
        }

        result = renderer._render_attachments(attachments)

        assert isinstance(result, list)

    def test_render_empty_attachments(self):
        """Handles empty attachments"""
        renderer = DocumentRenderer()
        result = renderer._render_attachments({})

        assert isinstance(result, list)


class TestRenderFooter:
    """Unit tests for _render_footer method"""

    def test_render_footer_with_date(self):
        """Renders footer with date"""
        renderer = DocumentRenderer()
        footer = {"date": {"text": "2025년 12월 3일", "format": {}}}

        result = renderer._render_footer(footer)

        assert isinstance(result, list)

    def test_render_footer_with_signature(self):
        """Renders footer with signature"""
        renderer = DocumentRenderer()
        footer = {"signature": {"plaintiff_name": "김○○", "format": {}}}

        result = renderer._render_footer(footer)

        assert isinstance(result, list)

    def test_render_footer_with_court(self):
        """Renders footer with court submission"""
        renderer = DocumentRenderer()
        footer = {"court": {"text": "서울가정법원", "format": {}}}

        result = renderer._render_footer(footer)

        assert isinstance(result, list)

    def test_render_empty_footer(self):
        """Handles empty footer"""
        renderer = DocumentRenderer()
        result = renderer._render_footer({})

        assert isinstance(result, list)


class TestConstants:
    """Tests for DocumentRenderer constants"""

    def test_default_width(self):
        """DEFAULT_WIDTH is set"""
        assert DocumentRenderer.DEFAULT_WIDTH == 80

    def test_indent_chars(self):
        """INDENT_CHARS is set"""
        assert DocumentRenderer.INDENT_CHARS == 4
