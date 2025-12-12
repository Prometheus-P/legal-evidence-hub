"""
Contract tests for Precedent API
012-precedent-integration: T053
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import status

from app.main import app
from app.db.schemas import PrecedentCase, PrecedentSearchResponse


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Mock authenticated headers"""
    return {"Authorization": "Bearer test_token"}


@pytest.fixture
def mock_user_id():
    """Mock user ID for authentication"""
    return "user_test_123"


@pytest.fixture
def mock_case():
    """Mock case data"""
    return Mock(
        id="case_123",
        title="이혼 소송",
        status="active"
    )


@pytest.fixture
def sample_precedent_response():
    """Sample precedent search response"""
    return PrecedentSearchResponse(
        precedents=[
            PrecedentCase(
                case_ref="2022다12345",
                court="대법원",
                decision_date="2023-03-15",
                case_type="이혼",
                summary="불륜으로 인한 이혼 소송에서 재산분할 비율 결정",
                key_factors=["불륜", "재산분할"],
                property_division_ratio="60:40",
                alimony_amount=30000000,
                similarity_score=0.87,
                source_url="https://www.law.go.kr/LSW/precInfoP.do?precSeq=12345"
            ),
        ],
        total=1,
        search_keywords=["불륜", "재산분할"]
    )


class TestPrecedentSearchAPI:
    """Test /cases/{case_id}/similar-precedents endpoint"""

    def test_search_similar_precedents_success(
        self, client, auth_headers, mock_case, sample_precedent_response
    ):
        """Test successful precedent search returns correct structure"""
        with patch('app.core.dependencies.get_current_user_id', return_value="user_123"), \
             patch('app.core.dependencies.verify_case_read_access'), \
             patch('app.services.precedent_service.PrecedentService') as mock_service:

            mock_service.return_value.search_similar_precedents.return_value = sample_precedent_response

            response = client.get(
                "/api/cases/case_123/similar-precedents",
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            # Verify response structure
            assert "precedents" in data
            assert "total" in data
            assert "search_keywords" in data
            assert len(data["precedents"]) == 1

            # Verify precedent structure
            precedent = data["precedents"][0]
            assert "case_ref" in precedent
            assert "court" in precedent
            assert "decision_date" in precedent
            assert "summary" in precedent
            assert "key_factors" in precedent
            assert "similarity_score" in precedent

    def test_search_with_query_params(self, client, auth_headers, sample_precedent_response):
        """Test search with limit and min_score parameters"""
        with patch('app.core.dependencies.get_current_user_id', return_value="user_123"), \
             patch('app.core.dependencies.verify_case_read_access'), \
             patch('app.services.precedent_service.PrecedentService') as mock_service:

            mock_service.return_value.search_similar_precedents.return_value = sample_precedent_response

            response = client.get(
                "/api/cases/case_123/similar-precedents?limit=5&min_score=0.7",
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_200_OK
            # Verify service was called with correct params
            mock_service.return_value.search_similar_precedents.assert_called_once()

    def test_search_empty_results(self, client, auth_headers):
        """Test search returning empty results"""
        with patch('app.core.dependencies.get_current_user_id', return_value="user_123"), \
             patch('app.core.dependencies.verify_case_read_access'), \
             patch('app.services.precedent_service.PrecedentService') as mock_service:

            empty_response = PrecedentSearchResponse(
                precedents=[],
                total=0,
                search_keywords=["이혼"]
            )
            mock_service.return_value.search_similar_precedents.return_value = empty_response

            response = client.get(
                "/api/cases/case_123/similar-precedents",
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["total"] == 0
            assert data["precedents"] == []

    def test_search_with_qdrant_warning(self, client, auth_headers):
        """Test search returns warning when Qdrant fails"""
        with patch('app.core.dependencies.get_current_user_id', return_value="user_123"), \
             patch('app.core.dependencies.verify_case_read_access'), \
             patch('app.services.precedent_service.PrecedentService') as mock_service:

            warning_response = PrecedentSearchResponse(
                precedents=[],
                total=0,
                search_keywords=[],
                warning="Qdrant 연결 실패 - 판례 검색을 사용할 수 없습니다"
            )
            mock_service.return_value.search_similar_precedents.return_value = warning_response

            response = client.get(
                "/api/cases/case_123/similar-precedents",
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "warning" in data
            assert data["warning"] is not None

    def test_search_unauthorized(self, client):
        """Test search without authentication returns 401"""
        response = client.get("/api/cases/case_123/similar-precedents")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_search_forbidden(self, client, auth_headers):
        """Test search without case access returns 403"""
        with patch('app.core.dependencies.get_current_user_id', return_value="user_123"), \
             patch('app.core.dependencies.verify_case_read_access') as mock_verify:

            from app.middleware import ForbiddenError
            mock_verify.side_effect = ForbiddenError("No access to case")

            response = client.get(
                "/api/cases/case_123/similar-precedents",
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_search_case_not_found(self, client, auth_headers):
        """Test search with non-existent case returns 404"""
        with patch('app.core.dependencies.get_current_user_id', return_value="user_123"), \
             patch('app.core.dependencies.verify_case_read_access'), \
             patch('app.services.precedent_service.PrecedentService') as mock_service:

            from app.middleware import NotFoundError
            mock_service.return_value.search_similar_precedents.side_effect = NotFoundError("Case not found")

            response = client.get(
                "/api/cases/nonexistent/similar-precedents",
                headers=auth_headers
            )

            assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAutoExtractPartyAPI:
    """Test /cases/{case_id}/parties/auto-extract endpoint"""

    def test_auto_extract_party_success(self, client, auth_headers):
        """Test successful party auto-extraction"""
        with patch('app.core.dependencies.get_current_user_id', return_value="user_123"), \
             patch('app.core.dependencies.verify_case_write_access'), \
             patch('app.services.party_service.PartyService') as mock_service:

            mock_service.return_value.create_auto_extracted_party.return_value = Mock(
                id="party_xyz789",
                name="김철수",
                is_duplicate=False,
                matched_party_id=None
            )

            response = client.post(
                "/api/cases/case_123/parties/auto-extract",
                headers=auth_headers,
                json={
                    "name": "김철수",
                    "type": "plaintiff",
                    "extraction_confidence": 0.85,
                    "source_evidence_id": "ev_abc123"
                }
            )

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert "id" in data
            assert "is_duplicate" in data
            assert data["is_duplicate"] is False

    def test_auto_extract_party_duplicate(self, client, auth_headers):
        """Test party auto-extraction with duplicate detection"""
        with patch('app.core.dependencies.get_current_user_id', return_value="user_123"), \
             patch('app.core.dependencies.verify_case_write_access'), \
             patch('app.services.party_service.PartyService') as mock_service:

            mock_service.return_value.create_auto_extracted_party.return_value = Mock(
                id="party_existing",
                name="김철수",
                is_duplicate=True,
                matched_party_id="party_existing"
            )

            response = client.post(
                "/api/cases/case_123/parties/auto-extract",
                headers=auth_headers,
                json={
                    "name": "김철수",
                    "type": "plaintiff",
                    "extraction_confidence": 0.85,
                    "source_evidence_id": "ev_abc123"
                }
            )

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["is_duplicate"] is True
            assert data["matched_party_id"] is not None

    def test_auto_extract_party_low_confidence(self, client, auth_headers):
        """Test party auto-extraction with low confidence fails"""
        with patch('app.core.dependencies.get_current_user_id', return_value="user_123"), \
             patch('app.core.dependencies.verify_case_write_access'):

            response = client.post(
                "/api/cases/case_123/parties/auto-extract",
                headers=auth_headers,
                json={
                    "name": "김철수",
                    "type": "plaintiff",
                    "extraction_confidence": 0.5,  # Below 0.7 threshold
                    "source_evidence_id": "ev_abc123"
                }
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestAutoExtractRelationshipAPI:
    """Test /cases/{case_id}/relationships/auto-extract endpoint"""

    def test_auto_extract_relationship_success(self, client, auth_headers):
        """Test successful relationship auto-extraction"""
        with patch('app.core.dependencies.get_current_user_id', return_value="user_123"), \
             patch('app.core.dependencies.verify_case_write_access'), \
             patch('app.services.relationship_service.RelationshipService') as mock_service:

            mock_service.return_value.create_auto_extracted_relationship.return_value = Mock(
                id="rel_xyz123",
                created=True
            )

            response = client.post(
                "/api/cases/case_123/relationships/auto-extract",
                headers=auth_headers,
                json={
                    "source_party_id": "party_abc",
                    "target_party_id": "party_def",
                    "type": "marriage",
                    "extraction_confidence": 0.92,
                    "evidence_text": "2010년 결혼..."
                }
            )

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert "id" in data
            assert data["created"] is True

    def test_auto_extract_relationship_low_confidence(self, client, auth_headers):
        """Test relationship auto-extraction with low confidence fails"""
        with patch('app.core.dependencies.get_current_user_id', return_value="user_123"), \
             patch('app.core.dependencies.verify_case_write_access'), \
             patch('app.services.relationship_service.RelationshipService') as mock_service:

            from app.middleware import ValidationError
            mock_service.return_value.create_auto_extracted_relationship.side_effect = \
                ValidationError("추출 신뢰도는 0.7 이상이어야 합니다")

            response = client.post(
                "/api/cases/case_123/relationships/auto-extract",
                headers=auth_headers,
                json={
                    "source_party_id": "party_abc",
                    "target_party_id": "party_def",
                    "type": "marriage",
                    "extraction_confidence": 0.5,
                    "evidence_text": "test"
                }
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_auto_extract_relationship_party_not_found(self, client, auth_headers):
        """Test relationship auto-extraction with non-existent party"""
        with patch('app.core.dependencies.get_current_user_id', return_value="user_123"), \
             patch('app.core.dependencies.verify_case_write_access'), \
             patch('app.services.relationship_service.RelationshipService') as mock_service:

            from app.middleware import NotFoundError
            mock_service.return_value.create_auto_extracted_relationship.side_effect = \
                NotFoundError("인물을 찾을 수 없습니다")

            response = client.post(
                "/api/cases/case_123/relationships/auto-extract",
                headers=auth_headers,
                json={
                    "source_party_id": "nonexistent",
                    "target_party_id": "party_def",
                    "type": "marriage",
                    "extraction_confidence": 0.85,
                    "evidence_text": "test"
                }
            )

            assert response.status_code == status.HTTP_404_NOT_FOUND
