"""
Unit tests for RAGOrchestrator Service
TDD - Improving test coverage for rag_orchestrator.py
"""

from unittest.mock import patch
from app.services.rag_orchestrator import RAGOrchestrator, get_rag_orchestrator


class TestRAGOrchestratorInit:
    """Unit tests for RAGOrchestrator initialization"""

    def test_init(self):
        """RAGOrchestrator initializes successfully"""
        orchestrator = RAGOrchestrator()
        assert orchestrator is not None


class TestPerformRagSearch:
    """Unit tests for perform_rag_search method"""

    @patch('app.services.rag_orchestrator.search_evidence_by_semantic')
    @patch('app.services.rag_orchestrator.search_legal_knowledge')
    def test_perform_rag_search_with_청구원인(self, mock_legal, mock_evidence):
        """Uses specialized query for 청구원인 section"""
        mock_evidence.return_value = [{"id": "ev1"}]
        mock_legal.return_value = [{"article_number": "840조"}]

        orchestrator = RAGOrchestrator()
        result = orchestrator.perform_rag_search(
            case_id="case123",
            sections=["청구원인", "청구취지"]
        )

        # Should search with fault-related query
        mock_evidence.assert_called_once()
        call_args = mock_evidence.call_args
        assert call_args.kwargs["case_id"] == "case123"
        assert call_args.kwargs["top_k"] == 10  # Higher for 청구원인

        # Should search legal for divorce grounds
        mock_legal.assert_called_once()
        assert "840조" in mock_legal.call_args.kwargs["query"]

        assert "evidence" in result
        assert "legal" in result

    @patch('app.services.rag_orchestrator.search_evidence_by_semantic')
    @patch('app.services.rag_orchestrator.search_legal_knowledge')
    def test_perform_rag_search_general_sections(self, mock_legal, mock_evidence):
        """Uses general query for other sections"""
        mock_evidence.return_value = []
        mock_legal.return_value = []

        orchestrator = RAGOrchestrator()
        result = orchestrator.perform_rag_search(
            case_id="case123",
            sections=["입증방법", "첨부서류"]
        )

        # Should use general query with lower top_k
        mock_evidence.assert_called_once()
        assert mock_evidence.call_args.kwargs["top_k"] == 5

        assert result == {"evidence": [], "legal": []}


class TestBuildQdrantFilter:
    """Unit tests for build_qdrant_filter method"""

    def test_build_filter_case_id_only(self):
        """Builds filter with case_id only"""
        orchestrator = RAGOrchestrator()
        filter_dict = orchestrator.build_qdrant_filter(case_id="case123")

        assert "must" in filter_dict
        assert len(filter_dict["must"]) == 1
        assert filter_dict["must"][0]["key"] == "case_id"
        assert filter_dict["must"][0]["match"]["value"] == "case123"

    def test_build_filter_with_labels(self):
        """Builds filter with case_id and labels"""
        orchestrator = RAGOrchestrator()
        filter_dict = orchestrator.build_qdrant_filter(
            case_id="case123",
            labels=["폭언", "협박"]
        )

        assert len(filter_dict["must"]) == 2
        # First condition is case_id
        assert filter_dict["must"][0]["key"] == "case_id"
        # Second condition is labels
        assert filter_dict["must"][1]["key"] == "labels"
        assert filter_dict["must"][1]["match"]["any"] == ["폭언", "협박"]

    def test_build_filter_empty_labels(self):
        """Empty labels list behaves like no labels"""
        orchestrator = RAGOrchestrator()
        filter_dict = orchestrator.build_qdrant_filter(
            case_id="case123",
            labels=[]
        )

        # Empty list is falsy, so no labels filter
        assert len(filter_dict["must"]) == 1


class TestFormatEvidenceContext:
    """Unit tests for format_evidence_context method"""

    def test_format_empty_evidence(self):
        """Returns placeholder for empty evidence"""
        orchestrator = RAGOrchestrator()
        result = orchestrator.format_evidence_context([])

        assert "증거 자료 없음" in result

    def test_format_single_evidence(self):
        """Formats single evidence document"""
        orchestrator = RAGOrchestrator()
        evidence = [{
            "chunk_id": "ev001",
            "document": "피고가 원고에게 폭언을 하였습니다.",
            "legal_categories": ["폭언"],
            "sender": "피고",
            "timestamp": "2024-01-15T14:30:00Z"
        }]

        result = orchestrator.format_evidence_context(evidence)

        assert "[갑 제1호증]" in result
        assert "ev001" in result
        assert "폭언" in result
        assert "피고" in result
        assert "2024-01-15" in result

    def test_format_multiple_evidence(self):
        """Formats multiple evidence documents"""
        orchestrator = RAGOrchestrator()
        evidence = [
            {"chunk_id": "ev001", "document": "내용1", "legal_categories": ["폭언"]},
            {"chunk_id": "ev002", "document": "내용2", "legal_categories": ["협박"]}
        ]

        result = orchestrator.format_evidence_context(evidence)

        assert "[갑 제1호증]" in result
        assert "[갑 제2호증]" in result
        assert "ev001" in result
        assert "ev002" in result

    def test_format_evidence_truncates_long_content(self):
        """Truncates content over 500 characters"""
        orchestrator = RAGOrchestrator()
        long_content = "x" * 1000
        evidence = [{"id": "ev001", "content": long_content}]

        result = orchestrator.format_evidence_context(evidence)

        assert "..." in result
        # Content should be truncated
        assert long_content not in result

    def test_format_evidence_missing_fields(self):
        """Handles missing fields gracefully"""
        orchestrator = RAGOrchestrator()
        evidence = [{"id": "ev001"}]  # Missing most fields

        result = orchestrator.format_evidence_context(evidence)

        assert "[갑 제1호증]" in result
        assert "N/A" in result  # Missing fields show N/A

    def test_format_evidence_fallback_fields(self):
        """Uses fallback field names"""
        orchestrator = RAGOrchestrator()
        evidence = [{
            "id": "ev001",  # Fallback for chunk_id
            "content": "내용",  # Fallback for document
            "labels": ["라벨"],  # Fallback for legal_categories
            "speaker": "화자"  # Fallback for sender
        }]

        result = orchestrator.format_evidence_context(evidence)

        assert "ev001" in result
        assert "내용" in result
        assert "라벨" in result
        assert "화자" in result


class TestFormatLegalContext:
    """Unit tests for format_legal_context method"""

    def test_format_empty_legal(self):
        """Returns placeholder for empty legal results"""
        orchestrator = RAGOrchestrator()
        result = orchestrator.format_legal_context([])

        assert "관련 법률 조문 없음" in result

    def test_format_single_legal_document(self):
        """Formats single legal document"""
        orchestrator = RAGOrchestrator()
        legal = [{
            "article_number": "제840조",
            "statute_name": "민법",
            "document": "재판상 이혼 원인..."
        }]

        result = orchestrator.format_legal_context(legal)

        assert "민법" in result
        assert "제840조" in result
        assert "재판상 이혼" in result

    def test_format_multiple_legal_documents(self):
        """Formats multiple legal documents"""
        orchestrator = RAGOrchestrator()
        legal = [
            {"article_number": "제840조", "statute_name": "민법", "document": "내용1"},
            {"article_number": "제843조", "statute_name": "민법", "document": "내용2"}
        ]

        result = orchestrator.format_legal_context(legal)

        assert "제840조" in result
        assert "제843조" in result

    def test_format_legal_fallback_text_field(self):
        """Uses 'text' field as fallback for 'document'"""
        orchestrator = RAGOrchestrator()
        legal = [{
            "article_number": "제840조",
            "statute_name": "민법",
            "text": "재판상 이혼 사유"  # Using text instead of document
        }]

        result = orchestrator.format_legal_context(legal)

        assert "재판상 이혼 사유" in result

    def test_format_legal_missing_article_number(self):
        """Skips documents without article_number"""
        orchestrator = RAGOrchestrator()
        legal = [
            {"statute_name": "민법", "document": "내용"}  # No article_number
        ]

        result = orchestrator.format_legal_context(legal)

        # Should return placeholder since no valid documents
        assert "관련 법률 조문 없음" in result

    def test_format_legal_missing_content(self):
        """Skips documents without content"""
        orchestrator = RAGOrchestrator()
        legal = [
            {"article_number": "제840조", "statute_name": "민법"}  # No content
        ]

        result = orchestrator.format_legal_context(legal)

        assert "관련 법률 조문 없음" in result

    def test_format_legal_default_statute_name(self):
        """Uses '민법' as default statute name"""
        orchestrator = RAGOrchestrator()
        legal = [
            {"article_number": "제123조", "document": "내용"}  # No statute_name
        ]

        result = orchestrator.format_legal_context(legal)

        assert "민법" in result  # Default


class TestFormatRagContext:
    """Unit tests for format_rag_context (legacy method)"""

    def test_format_empty_rag_results(self):
        """Returns placeholder for empty results"""
        orchestrator = RAGOrchestrator()
        result = orchestrator.format_rag_context([])

        assert "증거 자료 없음" in result

    def test_format_rag_results(self):
        """Formats RAG results using legacy field names"""
        orchestrator = RAGOrchestrator()
        results = [{
            "id": "ev001",
            "content": "증거 내용",
            "labels": ["폭언"],
            "speaker": "피고",
            "timestamp": "2024-01-15"
        }]

        result = orchestrator.format_rag_context(results)

        assert "[증거 1]" in result
        assert "ev001" in result
        assert "증거 내용" in result
        assert "폭언" in result

    def test_format_rag_context_truncates_long_content(self):
        """Truncates content over 500 characters"""
        orchestrator = RAGOrchestrator()
        long_content = "y" * 1000
        results = [{"id": "ev001", "content": long_content}]

        result = orchestrator.format_rag_context(results)

        assert "..." in result

    def test_format_rag_context_missing_id(self):
        """Generates default ID when missing"""
        orchestrator = RAGOrchestrator()
        results = [{"content": "내용"}]  # No id

        result = orchestrator.format_rag_context(results)

        assert "evidence_1" in result


class TestGetRagOrchestrator:
    """Unit tests for get_rag_orchestrator singleton function"""

    def test_get_rag_orchestrator_returns_instance(self):
        """Returns RAGOrchestrator instance"""
        import app.services.rag_orchestrator as module
        module._rag_orchestrator = None  # Reset singleton

        result = get_rag_orchestrator()

        assert isinstance(result, RAGOrchestrator)

    def test_get_rag_orchestrator_returns_same_instance(self):
        """Returns same instance on multiple calls (singleton)"""
        import app.services.rag_orchestrator as module
        module._rag_orchestrator = None

        result1 = get_rag_orchestrator()
        result2 = get_rag_orchestrator()

        assert result1 is result2
