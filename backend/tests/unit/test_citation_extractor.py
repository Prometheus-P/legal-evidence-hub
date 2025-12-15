"""
Unit tests for CitationExtractor Service
TDD - Improving test coverage for citation_extractor.py
"""

from app.services.citation_extractor import CitationExtractor, get_citation_extractor
from app.db.schemas import DraftCitation


class TestCitationExtractorInit:
    """Unit tests for CitationExtractor initialization"""

    def test_init(self):
        """CitationExtractor initializes successfully"""
        extractor = CitationExtractor()
        assert extractor is not None


class TestExtractCitations:
    """Unit tests for extract_citations method"""

    def test_extract_empty_results(self):
        """Returns empty list for empty RAG results"""
        extractor = CitationExtractor()
        result = extractor.extract_citations([])
        assert result == []

    def test_extract_single_citation(self):
        """Extracts citation from single RAG result"""
        extractor = CitationExtractor()
        rag_results = [{
            "evidence_id": "EV-001",
            "content": "피고가 원고에게 폭언을 하였습니다.",
            "labels": ["폭언"]
        }]

        result = extractor.extract_citations(rag_results)

        assert len(result) == 1
        assert isinstance(result[0], DraftCitation)
        assert result[0].evidence_id == "EV-001"
        assert result[0].labels == ["폭언"]

    def test_extract_multiple_citations(self):
        """Extracts citations from multiple RAG results"""
        extractor = CitationExtractor()
        rag_results = [
            {"evidence_id": "EV-001", "content": "내용1", "labels": ["폭언"]},
            {"evidence_id": "EV-002", "content": "내용2", "labels": ["협박"]},
            {"evidence_id": "EV-003", "content": "내용3", "labels": ["불륜"]}
        ]

        result = extractor.extract_citations(rag_results)

        assert len(result) == 3
        assert result[0].evidence_id == "EV-001"
        assert result[1].evidence_id == "EV-002"
        assert result[2].evidence_id == "EV-003"

    def test_extract_uses_id_fallback(self):
        """Uses 'id' field if 'evidence_id' not present"""
        extractor = CitationExtractor()
        rag_results = [{
            "id": "ev123",  # Using 'id' instead of 'evidence_id'
            "content": "내용",
            "labels": []
        }]

        result = extractor.extract_citations(rag_results)

        assert result[0].evidence_id == "ev123"

    def test_extract_handles_missing_fields(self):
        """Handles missing optional fields gracefully"""
        extractor = CitationExtractor()
        rag_results = [{"evidence_id": "EV-001"}]  # Missing content and labels

        result = extractor.extract_citations(rag_results)

        assert len(result) == 1
        assert result[0].evidence_id == "EV-001"
        assert result[0].snippet == ""
        assert result[0].labels == []

    def test_extract_truncates_long_content(self):
        """Truncates content over 200 characters"""
        extractor = CitationExtractor()
        long_content = "x" * 500
        rag_results = [{
            "evidence_id": "EV-001",
            "content": long_content,
            "labels": []
        }]

        result = extractor.extract_citations(rag_results)

        assert len(result[0].snippet) == 203  # 200 + "..."
        assert result[0].snippet.endswith("...")


class TestCreateSnippet:
    """Unit tests for _create_snippet method"""

    def test_short_content_unchanged(self):
        """Short content returned unchanged"""
        extractor = CitationExtractor()
        content = "짧은 내용"

        result = extractor._create_snippet(content)

        assert result == content

    def test_exact_max_length(self):
        """Content at exactly max length not truncated"""
        extractor = CitationExtractor()
        content = "x" * 200

        result = extractor._create_snippet(content)

        assert result == content
        assert len(result) == 200

    def test_truncates_over_max_length(self):
        """Content over max length is truncated with ellipsis"""
        extractor = CitationExtractor()
        content = "y" * 250

        result = extractor._create_snippet(content)

        assert len(result) == 203
        assert result.endswith("...")

    def test_custom_max_length(self):
        """Respects custom max_length parameter"""
        extractor = CitationExtractor()
        content = "z" * 100

        result = extractor._create_snippet(content, max_length=50)

        assert len(result) == 53  # 50 + "..."
        assert result.endswith("...")


class TestParseCitationRefs:
    """Unit tests for parse_citation_refs method"""

    def test_parse_empty_text(self):
        """Returns empty list for empty text"""
        extractor = CitationExtractor()
        result = extractor.parse_citation_refs("")
        assert result == []

    def test_parse_no_citations(self):
        """Returns empty list when no citations in text"""
        extractor = CitationExtractor()
        text = "이것은 일반적인 텍스트입니다."
        result = extractor.parse_citation_refs(text)
        assert result == []

    def test_parse_single_citation(self):
        """Extracts single citation reference"""
        extractor = CitationExtractor()
        text = "피고는 폭언을 하였습니다 [갑 제1호증]."

        result = extractor.parse_citation_refs(text)

        assert len(result) == 1
        assert "[갑 제1호증]" in result

    def test_parse_multiple_citations(self):
        """Extracts multiple citation references"""
        extractor = CitationExtractor()
        text = "피고의 행위 [갑 제1호증]와 발언 [갑 제2호증]은 증명됩니다."

        result = extractor.parse_citation_refs(text)

        assert len(result) == 2
        assert "[갑 제1호증]" in result
        assert "[갑 제2호증]" in result

    def test_parse_removes_duplicates(self):
        """Removes duplicate citation references"""
        extractor = CitationExtractor()
        text = "[갑 제1호증] 내용 [갑 제1호증] 다시 언급"

        result = extractor.parse_citation_refs(text)

        assert len(result) == 1

    def test_parse_을_citations(self):
        """Extracts 을 (defendant's) citations"""
        extractor = CitationExtractor()
        text = "피고 측 증거 [을 제1호증]를 제출합니다."

        result = extractor.parse_citation_refs(text)

        assert len(result) == 1
        assert "[을 제1호증]" in result

    def test_parse_citation_with_suffix(self):
        """Extracts citations with suffix (예: 갑 제1호증의2)"""
        extractor = CitationExtractor()
        text = "녹음 파일 [갑 제3호증의2]"

        result = extractor.parse_citation_refs(text)

        assert len(result) == 1
        assert "[갑 제3호증의2]" in result

    def test_parse_mixed_citations(self):
        """Extracts mixed 갑/을 citations"""
        extractor = CitationExtractor()
        text = "원고 증거 [갑 제1호증] 및 피고 증거 [을 제1호증]"

        result = extractor.parse_citation_refs(text)

        assert len(result) == 2


class TestMapCitationsToEvidence:
    """Unit tests for map_citations_to_evidence method"""

    def test_map_empty_inputs(self):
        """Returns empty dict for empty inputs"""
        extractor = CitationExtractor()
        result = extractor.map_citations_to_evidence([], [])
        assert result == {}

    def test_map_single_citation(self):
        """Maps single citation to evidence"""
        extractor = CitationExtractor()
        citation_refs = ["[갑 제1호증]"]
        rag_results = [{"evidence_id": "EV-001"}]

        result = extractor.map_citations_to_evidence(citation_refs, rag_results)

        assert "[갑 제1호증]" in result
        assert result["[갑 제1호증]"] == "EV-001"

    def test_map_multiple_citations(self):
        """Maps multiple citations to evidence"""
        extractor = CitationExtractor()
        citation_refs = ["[갑 제1호증]", "[갑 제2호증]", "[갑 제3호증]"]
        rag_results = [
            {"evidence_id": "EV-001"},
            {"evidence_id": "EV-002"},
            {"evidence_id": "EV-003"}
        ]

        result = extractor.map_citations_to_evidence(citation_refs, rag_results)

        assert result["[갑 제1호증]"] == "EV-001"
        assert result["[갑 제2호증]"] == "EV-002"
        assert result["[갑 제3호증]"] == "EV-003"

    def test_map_uses_id_fallback(self):
        """Uses 'id' field if 'evidence_id' not present"""
        extractor = CitationExtractor()
        citation_refs = ["[갑 제1호증]"]
        rag_results = [{"id": "ev123"}]  # Using 'id'

        result = extractor.map_citations_to_evidence(citation_refs, rag_results)

        assert result["[갑 제1호증]"] == "ev123"


class TestGetCitationExtractor:
    """Unit tests for get_citation_extractor singleton function"""

    def test_returns_instance(self):
        """Returns CitationExtractor instance"""
        import app.services.citation_extractor as module
        module._citation_extractor = None  # Reset singleton

        result = get_citation_extractor()

        assert isinstance(result, CitationExtractor)

    def test_returns_same_instance(self):
        """Returns same instance on multiple calls (singleton)"""
        import app.services.citation_extractor as module
        module._citation_extractor = None

        result1 = get_citation_extractor()
        result2 = get_citation_extractor()

        assert result1 is result2
