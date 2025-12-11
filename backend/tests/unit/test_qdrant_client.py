"""
Unit tests for Qdrant utilities
009-mvp-gap-closure: US4 - CI 테스트 커버리지 정상화
"""

import pytest
from unittest.mock import MagicMock, patch


class TestGetCollectionName:
    """Unit tests for _get_collection_name function"""

    def test_get_collection_name_returns_prefixed_name(self):
        """Returns collection name with prefix"""
        from app.utils.qdrant import _get_collection_name

        result = _get_collection_name("case_123")

        assert "case_123" in result

    def test_get_collection_name_different_cases(self):
        """Returns unique names for different cases"""
        from app.utils.qdrant import _get_collection_name

        result1 = _get_collection_name("case_123")
        result2 = _get_collection_name("case_456")

        assert result1 != result2


class TestSearchEvidenceBySemantic:
    """Unit tests for search_evidence_by_semantic function"""

    @patch('app.utils.qdrant._get_qdrant_client')
    @patch('app.utils.qdrant.generate_embedding')
    def test_search_returns_empty_when_collection_not_exists(
        self, mock_embedding, mock_client
    ):
        """Returns empty list when collection doesn't exist"""
        from app.utils.qdrant import search_evidence_by_semantic

        # Mock client with no collections
        client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        client.get_collections.return_value = mock_collections
        mock_client.return_value = client

        result = search_evidence_by_semantic("case_123", "테스트 쿼리")

        assert result == []

    @patch('app.utils.qdrant._get_qdrant_client')
    @patch('app.utils.qdrant.generate_embedding')
    def test_search_returns_results_with_scores(
        self, mock_embedding, mock_client
    ):
        """Returns results with similarity scores"""
        from app.utils.qdrant import search_evidence_by_semantic, _get_collection_name

        # Mock embedding
        mock_embedding.return_value = [0.1] * 1536

        # Mock collection exists
        mock_collection = MagicMock()
        mock_collection.name = _get_collection_name("case_123")

        # Mock search results
        mock_point = MagicMock()
        mock_point.payload = {
            "evidence_id": "ev_001",
            "content": "테스트 증거",
            "labels": ["폭언"]
        }
        mock_point.score = 0.95

        mock_query_result = MagicMock()
        mock_query_result.points = [mock_point]

        client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        client.get_collections.return_value = mock_collections
        client.query_points.return_value = mock_query_result
        mock_client.return_value = client

        result = search_evidence_by_semantic("case_123", "테스트 쿼리")

        assert len(result) == 1
        assert result[0]["evidence_id"] == "ev_001"
        assert result[0]["_score"] == 0.95

    @patch('app.utils.qdrant._get_qdrant_client')
    @patch('app.utils.qdrant.generate_embedding')
    def test_search_handles_exception_gracefully(
        self, mock_embedding, mock_client
    ):
        """Returns empty list on exception"""
        from app.utils.qdrant import search_evidence_by_semantic

        # Mock client that throws exception on get_collections
        client = MagicMock()
        client.get_collections.side_effect = Exception("Connection error")
        mock_client.return_value = client

        result = search_evidence_by_semantic("case_123", "테스트 쿼리")

        assert result == []

    @patch('app.utils.qdrant._get_qdrant_client')
    @patch('app.utils.qdrant.generate_embedding')
    def test_search_applies_filters(
        self, mock_embedding, mock_client
    ):
        """Applies filter conditions to search"""
        from app.utils.qdrant import search_evidence_by_semantic, _get_collection_name

        mock_embedding.return_value = [0.1] * 1536

        mock_collection = MagicMock()
        mock_collection.name = _get_collection_name("case_123")

        mock_query_result = MagicMock()
        mock_query_result.points = []

        client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        client.get_collections.return_value = mock_collections
        client.query_points.return_value = mock_query_result
        mock_client.return_value = client

        # Search with filters
        search_evidence_by_semantic(
            "case_123",
            "테스트 쿼리",
            filters={"labels": ["폭언", "불륜"]}
        )

        # Verify query_points was called
        client.query_points.assert_called_once()
        call_kwargs = client.query_points.call_args[1]
        assert call_kwargs["query_filter"] is not None


class TestIndexEvidenceDocument:
    """Unit tests for index_evidence_document function"""

    @patch('app.utils.qdrant._get_qdrant_client')
    @patch('app.utils.qdrant.generate_embedding')
    @patch('app.utils.qdrant.create_case_collection')
    def test_index_creates_collection_if_not_exists(
        self, mock_create, mock_embedding, mock_client
    ):
        """Creates collection if it doesn't exist"""
        from app.utils.qdrant import index_evidence_document

        mock_embedding.return_value = [0.1] * 1536

        client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        client.get_collections.return_value = mock_collections
        mock_client.return_value = client

        doc = {
            "id": "ev_001",
            "content": "테스트 증거 내용"
        }

        index_evidence_document("case_123", doc)

        mock_create.assert_called_once_with("case_123")

    @patch('app.utils.qdrant._get_qdrant_client')
    def test_index_raises_without_id(self, mock_client):
        """Raises ValueError without document id"""
        from app.utils.qdrant import index_evidence_document, _get_collection_name

        mock_collection = MagicMock()
        mock_collection.name = _get_collection_name("case_123")

        client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        client.get_collections.return_value = mock_collections
        mock_client.return_value = client

        doc = {"content": "테스트"}  # No id field

        with pytest.raises(ValueError, match="id"):
            index_evidence_document("case_123", doc)

    @patch('app.utils.qdrant._get_qdrant_client')
    def test_index_raises_without_vector_or_content(self, mock_client):
        """Raises ValueError without vector or content"""
        from app.utils.qdrant import index_evidence_document, _get_collection_name

        mock_collection = MagicMock()
        mock_collection.name = _get_collection_name("case_123")

        client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        client.get_collections.return_value = mock_collections
        mock_client.return_value = client

        doc = {"id": "ev_001"}  # No vector or content

        with pytest.raises(ValueError, match="vector"):
            index_evidence_document("case_123", doc)


class TestCreateCaseCollection:
    """Unit tests for create_case_collection function"""

    @patch('app.utils.qdrant._get_qdrant_client')
    def test_create_returns_true_if_exists(self, mock_client):
        """Returns True if collection already exists"""
        from app.utils.qdrant import create_case_collection, _get_collection_name

        mock_collection = MagicMock()
        mock_collection.name = _get_collection_name("case_123")

        client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        client.get_collections.return_value = mock_collections
        mock_client.return_value = client

        result = create_case_collection("case_123")

        assert result is True
        client.create_collection.assert_not_called()

    @patch('app.utils.qdrant._get_qdrant_client')
    def test_create_creates_new_collection(self, mock_client):
        """Creates new collection if doesn't exist"""
        from app.utils.qdrant import create_case_collection

        client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        client.get_collections.return_value = mock_collections
        mock_client.return_value = client

        result = create_case_collection("case_123")

        assert result is True
        client.create_collection.assert_called_once()


class TestDeleteCaseCollection:
    """Unit tests for delete_case_collection function"""

    @patch('app.utils.qdrant._get_qdrant_client')
    def test_delete_returns_false_if_not_exists(self, mock_client):
        """Returns False if collection doesn't exist"""
        from app.utils.qdrant import delete_case_collection

        client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        client.get_collections.return_value = mock_collections
        mock_client.return_value = client

        result = delete_case_collection("case_123")

        assert result is False

    @patch('app.utils.qdrant._get_qdrant_client')
    def test_delete_deletes_existing_collection(self, mock_client):
        """Deletes existing collection"""
        from app.utils.qdrant import delete_case_collection, _get_collection_name

        mock_collection = MagicMock()
        mock_collection.name = _get_collection_name("case_123")

        client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        client.get_collections.return_value = mock_collections
        mock_client.return_value = client

        result = delete_case_collection("case_123")

        assert result is True
        client.delete_collection.assert_called_once()

    @patch('app.utils.qdrant._get_qdrant_client')
    def test_delete_returns_false_on_exception(self, mock_client):
        """Returns False on exception"""
        from app.utils.qdrant import delete_case_collection, _get_collection_name

        mock_collection = MagicMock()
        mock_collection.name = _get_collection_name("case_123")

        client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        client.get_collections.return_value = mock_collections
        client.delete_collection.side_effect = Exception("Delete error")
        mock_client.return_value = client

        result = delete_case_collection("case_123")

        assert result is False


class TestGetAllDocumentsInCase:
    """Unit tests for get_all_documents_in_case function"""

    @patch('app.utils.qdrant._get_qdrant_client')
    def test_returns_empty_if_collection_not_exists(self, mock_client):
        """Returns empty list if collection doesn't exist"""
        from app.utils.qdrant import get_all_documents_in_case

        client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        client.get_collections.return_value = mock_collections
        mock_client.return_value = client

        result = get_all_documents_in_case("case_123")

        assert result == []

    @patch('app.utils.qdrant._get_qdrant_client')
    def test_returns_documents(self, mock_client):
        """Returns all documents in collection"""
        from app.utils.qdrant import get_all_documents_in_case, _get_collection_name

        mock_collection = MagicMock()
        mock_collection.name = _get_collection_name("case_123")

        mock_point = MagicMock()
        mock_point.payload = {"evidence_id": "ev_001", "content": "테스트"}

        client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        client.get_collections.return_value = mock_collections
        client.scroll.return_value = ([mock_point], None)
        mock_client.return_value = client

        result = get_all_documents_in_case("case_123")

        assert len(result) == 1
        assert result[0]["evidence_id"] == "ev_001"

    @patch('app.utils.qdrant._get_qdrant_client')
    def test_returns_empty_on_exception(self, mock_client):
        """Returns empty list on exception"""
        from app.utils.qdrant import get_all_documents_in_case, _get_collection_name

        mock_collection = MagicMock()
        mock_collection.name = _get_collection_name("case_123")

        client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        client.get_collections.return_value = mock_collections
        client.scroll.side_effect = Exception("Scroll error")
        mock_client.return_value = client

        result = get_all_documents_in_case("case_123")

        assert result == []


class TestSearchLegalKnowledge:
    """Unit tests for search_legal_knowledge function"""

    @patch('app.utils.qdrant._get_qdrant_client')
    @patch('app.utils.qdrant.generate_embedding')
    def test_returns_empty_if_collection_not_exists(
        self, mock_embedding, mock_client
    ):
        """Returns empty list if legal collection doesn't exist"""
        from app.utils.qdrant import search_legal_knowledge

        client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        client.get_collections.return_value = mock_collections
        mock_client.return_value = client

        result = search_legal_knowledge("이혼 사유")

        assert result == []

    @patch('app.utils.qdrant._get_qdrant_client')
    @patch('app.utils.qdrant.generate_embedding')
    def test_returns_legal_documents_with_scores(
        self, mock_embedding, mock_client
    ):
        """Returns legal documents with scores"""
        from app.utils.qdrant import search_legal_knowledge, LEGAL_KNOWLEDGE_COLLECTION

        mock_embedding.return_value = [0.1] * 1536

        mock_collection = MagicMock()
        mock_collection.name = LEGAL_KNOWLEDGE_COLLECTION

        mock_point = MagicMock()
        mock_point.payload = {
            "doc_type": "statute",
            "title": "민법 제840조",
            "content": "재판상 이혼 사유"
        }
        mock_point.score = 0.9

        mock_query_result = MagicMock()
        mock_query_result.points = [mock_point]

        client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        client.get_collections.return_value = mock_collections
        client.query_points.return_value = mock_query_result
        mock_client.return_value = client

        result = search_legal_knowledge("이혼 사유")

        assert len(result) == 1
        assert result[0]["title"] == "민법 제840조"
        assert result[0]["_score"] == 0.9

    @patch('app.utils.qdrant._get_qdrant_client')
    @patch('app.utils.qdrant.generate_embedding')
    def test_applies_doc_type_filter(
        self, mock_embedding, mock_client
    ):
        """Applies doc_type filter"""
        from app.utils.qdrant import search_legal_knowledge, LEGAL_KNOWLEDGE_COLLECTION

        mock_embedding.return_value = [0.1] * 1536

        mock_collection = MagicMock()
        mock_collection.name = LEGAL_KNOWLEDGE_COLLECTION

        mock_query_result = MagicMock()
        mock_query_result.points = []

        client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        client.get_collections.return_value = mock_collections
        client.query_points.return_value = mock_query_result
        mock_client.return_value = client

        search_legal_knowledge("이혼", doc_type="statute")

        call_kwargs = client.query_points.call_args[1]
        assert call_kwargs["query_filter"] is not None

    @patch('app.utils.qdrant._get_qdrant_client')
    @patch('app.utils.qdrant.generate_embedding')
    def test_returns_empty_on_exception(
        self, mock_embedding, mock_client
    ):
        """Returns empty list on exception"""
        from app.utils.qdrant import search_legal_knowledge

        # Mock client that throws exception on get_collections
        client = MagicMock()
        client.get_collections.side_effect = Exception("Connection error")
        mock_client.return_value = client

        result = search_legal_knowledge("이혼")

        assert result == []


class TestGetTemplateByType:
    """Unit tests for get_template_by_type function"""

    @patch('app.utils.qdrant._get_qdrant_client')
    def test_returns_none_if_collection_not_exists(self, mock_client):
        """Returns None if template collection doesn't exist"""
        from app.utils.qdrant import get_template_by_type

        client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = []
        client.get_collections.return_value = mock_collections
        mock_client.return_value = client

        result = get_template_by_type("이혼소장")

        assert result is None

    @patch('app.utils.qdrant._get_qdrant_client')
    def test_returns_template(self, mock_client):
        """Returns template dict"""
        from app.utils.qdrant import get_template_by_type, TEMPLATE_COLLECTION

        mock_collection = MagicMock()
        mock_collection.name = TEMPLATE_COLLECTION

        mock_point = MagicMock()
        mock_point.id = 123
        mock_point.payload = {
            "template_type": "이혼소장",
            "version": "1.0",
            "description": "이혼 소장 양식",
            "schema": {"sections": []},
            "example": {"content": "예시"},
            "applicable_cases": ["divorce"]
        }

        client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        client.get_collections.return_value = mock_collections
        client.scroll.return_value = ([mock_point], None)
        mock_client.return_value = client

        result = get_template_by_type("이혼소장")

        assert result is not None
        assert result["template_type"] == "이혼소장"
        assert result["version"] == "1.0"

    @patch('app.utils.qdrant._get_qdrant_client')
    def test_returns_none_if_not_found(self, mock_client):
        """Returns None if template not found"""
        from app.utils.qdrant import get_template_by_type, TEMPLATE_COLLECTION

        mock_collection = MagicMock()
        mock_collection.name = TEMPLATE_COLLECTION

        client = MagicMock()
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        client.get_collections.return_value = mock_collections
        client.scroll.return_value = ([], None)
        mock_client.return_value = client

        result = get_template_by_type("존재하지않는템플릿")

        assert result is None

    @patch('app.utils.qdrant._get_qdrant_client')
    def test_returns_none_on_exception(self, mock_client):
        """Returns None on exception"""
        from app.utils.qdrant import get_template_by_type

        # Mock client that throws exception on get_collections
        client = MagicMock()
        client.get_collections.side_effect = Exception("Connection error")
        mock_client.return_value = client

        result = get_template_by_type("이혼소장")

        assert result is None


class TestGetTemplateSchemaForPrompt:
    """Unit tests for get_template_schema_for_prompt function"""

    @patch('app.utils.qdrant.get_template_by_type')
    def test_returns_json_schema(self, mock_get_template):
        """Returns JSON formatted schema"""
        from app.utils.qdrant import get_template_schema_for_prompt

        mock_get_template.return_value = {
            "schema": {"sections": ["청구취지", "청구원인"]}
        }

        result = get_template_schema_for_prompt("이혼소장")

        assert result is not None
        assert "sections" in result
        assert "청구취지" in result

    @patch('app.utils.qdrant.get_template_by_type')
    def test_returns_none_if_no_template(self, mock_get_template):
        """Returns None if template not found"""
        from app.utils.qdrant import get_template_schema_for_prompt

        mock_get_template.return_value = None

        result = get_template_schema_for_prompt("없는템플릿")

        assert result is None

    @patch('app.utils.qdrant.get_template_by_type')
    def test_returns_none_if_no_schema(self, mock_get_template):
        """Returns None if template has no schema"""
        from app.utils.qdrant import get_template_schema_for_prompt

        mock_get_template.return_value = {
            "template_type": "이혼소장",
            "schema": None
        }

        result = get_template_schema_for_prompt("이혼소장")

        assert result is None


class TestGetTemplateExampleForPrompt:
    """Unit tests for get_template_example_for_prompt function"""

    @patch('app.utils.qdrant.get_template_by_type')
    def test_returns_json_example(self, mock_get_template):
        """Returns JSON formatted example"""
        from app.utils.qdrant import get_template_example_for_prompt

        mock_get_template.return_value = {
            "example": {"content": "예시 내용"}
        }

        result = get_template_example_for_prompt("이혼소장")

        assert result is not None
        assert "content" in result
        assert "예시" in result

    @patch('app.utils.qdrant.get_template_by_type')
    def test_returns_none_if_no_template(self, mock_get_template):
        """Returns None if template not found"""
        from app.utils.qdrant import get_template_example_for_prompt

        mock_get_template.return_value = None

        result = get_template_example_for_prompt("없는템플릿")

        assert result is None


class TestBackwardCompatibilityAliases:
    """Unit tests for backward compatibility aliases"""

    @patch('app.utils.qdrant.delete_case_collection')
    def test_delete_case_index_calls_delete_case_collection(self, mock_delete):
        """delete_case_index is alias for delete_case_collection"""
        from app.utils.qdrant import delete_case_index

        mock_delete.return_value = True

        result = delete_case_index("case_123")

        mock_delete.assert_called_once_with("case_123")
        assert result is True

    @patch('app.utils.qdrant.create_case_collection')
    def test_create_case_index_calls_create_case_collection(self, mock_create):
        """create_case_index is alias for create_case_collection"""
        from app.utils.qdrant import create_case_index

        mock_create.return_value = True

        result = create_case_index("case_123")

        mock_create.assert_called_once_with("case_123")
        assert result is True
