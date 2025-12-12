"""
Unit tests for PrecedentService
012-precedent-integration: T052
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.services.precedent_service import PrecedentService
from app.db.schemas import PrecedentCase, PrecedentSearchResponse


class TestPrecedentService:
    """Test suite for PrecedentService"""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        return Mock()

    @pytest.fixture
    def service(self, mock_db):
        """Create PrecedentService instance with mocked dependencies"""
        with patch('app.services.precedent_service.CaseRepository') as mock_case_repo, \
             patch('app.services.precedent_service.EvidenceService') as mock_evidence_service:
            mock_case_repo.return_value.get_by_id.return_value = Mock(id="case_123")
            service = PrecedentService(mock_db)
            return service

    @pytest.fixture
    def sample_precedents(self):
        """Sample precedent data for testing"""
        return [
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
            PrecedentCase(
                case_ref="2021다67890",
                court="서울고등법원",
                decision_date="2022-11-20",
                case_type="이혼",
                summary="가정폭력으로 인한 이혼 소송",
                key_factors=["가정폭력", "위자료"],
                property_division_ratio="70:30",
                alimony_amount=50000000,
                similarity_score=0.75,
                source_url="https://www.law.go.kr/LSW/precInfoP.do?precSeq=67890"
            ),
        ]

    # ============================================
    # search_similar_precedents tests
    # ============================================

    def test_search_similar_precedents_success(self, service, sample_precedents):
        """Test successful precedent search"""
        with patch.object(service, '_search_qdrant') as mock_search:
            mock_search.return_value = sample_precedents

            result = service.search_similar_precedents(
                case_id="case_123",
                limit=10,
                min_score=0.5
            )

            assert isinstance(result, PrecedentSearchResponse)
            assert len(result.precedents) == 2
            assert result.total == 2
            assert result.precedents[0].case_ref == "2022다12345"
            assert result.precedents[0].similarity_score == 0.87

    def test_search_similar_precedents_empty_result(self, service):
        """Test search with no results"""
        with patch.object(service, '_search_qdrant') as mock_search:
            mock_search.return_value = []

            result = service.search_similar_precedents(
                case_id="case_123",
                limit=10,
                min_score=0.5
            )

            assert isinstance(result, PrecedentSearchResponse)
            assert len(result.precedents) == 0
            assert result.total == 0

    def test_search_similar_precedents_filters_by_min_score(self, service, sample_precedents):
        """Test that results are filtered by minimum score"""
        with patch.object(service, '_search_qdrant') as mock_search:
            # Only return precedent with score >= 0.8
            mock_search.return_value = [p for p in sample_precedents if p.similarity_score >= 0.8]

            result = service.search_similar_precedents(
                case_id="case_123",
                limit=10,
                min_score=0.8
            )

            assert len(result.precedents) == 1
            assert result.precedents[0].case_ref == "2022다12345"

    def test_search_similar_precedents_respects_limit(self, service, sample_precedents):
        """Test that results respect the limit parameter"""
        with patch.object(service, '_search_qdrant') as mock_search:
            mock_search.return_value = sample_precedents[:1]

            result = service.search_similar_precedents(
                case_id="case_123",
                limit=1,
                min_score=0.5
            )

            assert len(result.precedents) == 1

    def test_search_similar_precedents_case_not_found(self, mock_db):
        """Test search with non-existent case"""
        with patch('app.services.precedent_service.CaseRepository') as mock_case_repo:
            mock_case_repo.return_value.get_by_id.return_value = None
            service = PrecedentService(mock_db)

            from app.middleware import NotFoundError
            with pytest.raises(NotFoundError):
                service.search_similar_precedents(
                    case_id="nonexistent_case",
                    limit=10,
                    min_score=0.5
                )

    def test_search_similar_precedents_qdrant_failure(self, service):
        """Test graceful handling of Qdrant connection failure"""
        with patch.object(service, '_search_qdrant') as mock_search:
            mock_search.side_effect = Exception("Qdrant connection failed")

            result = service.search_similar_precedents(
                case_id="case_123",
                limit=10,
                min_score=0.5
            )

            # Should return empty result with warning, not raise exception
            assert isinstance(result, PrecedentSearchResponse)
            assert len(result.precedents) == 0
            assert result.warning is not None

    # ============================================
    # get_fault_types tests
    # ============================================

    def test_get_fault_types_extracts_categories(self, service):
        """Test fault type extraction from case evidence"""
        with patch.object(service.evidence_service, 'get_evidence_list') as mock_get:
            mock_evidence = [
                Mock(ai_tags={"categories": ["불륜", "폭언"]}),
                Mock(ai_tags={"categories": ["재산은닉"]}),
            ]
            mock_get.return_value = mock_evidence

            fault_types = service.get_fault_types("case_123")

            assert "불륜" in fault_types
            assert "폭언" in fault_types
            assert "재산은닉" in fault_types

    def test_get_fault_types_handles_empty_evidence(self, service):
        """Test fault type extraction with no evidence"""
        with patch.object(service.evidence_service, 'get_evidence_list') as mock_get:
            mock_get.return_value = []

            fault_types = service.get_fault_types("case_123")

            assert fault_types == []

    def test_get_fault_types_handles_missing_tags(self, service):
        """Test fault type extraction when evidence has no tags"""
        with patch.object(service.evidence_service, 'get_evidence_list') as mock_get:
            mock_evidence = [
                Mock(ai_tags=None),
                Mock(ai_tags={}),
            ]
            mock_get.return_value = mock_evidence

            fault_types = service.get_fault_types("case_123")

            assert fault_types == []

    # ============================================
    # _build_search_query tests
    # ============================================

    def test_build_search_query_combines_fault_types(self, service):
        """Test search query construction from fault types"""
        with patch.object(service, 'get_fault_types') as mock_fault:
            mock_fault.return_value = ["불륜", "재산분할"]

            query = service._build_search_query("case_123")

            assert "불륜" in query
            assert "재산분할" in query

    def test_build_search_query_handles_no_fault_types(self, service):
        """Test search query with no fault types (uses default)"""
        with patch.object(service, 'get_fault_types') as mock_fault:
            mock_fault.return_value = []

            query = service._build_search_query("case_123")

            # Should return default query
            assert query == "이혼 재산분할 위자료"

    # ============================================
    # PrecedentCase model tests
    # ============================================

    def test_precedent_case_model(self):
        """Test PrecedentCase Pydantic model validation"""
        precedent = PrecedentCase(
            case_ref="2022다12345",
            court="대법원",
            decision_date="2023-03-15",
            case_type="이혼",
            summary="테스트 요약",
            key_factors=["불륜"],
            similarity_score=0.85
        )

        assert precedent.case_ref == "2022다12345"
        assert precedent.similarity_score == 0.85
        assert precedent.property_division_ratio is None
        assert precedent.alimony_amount is None

    def test_precedent_case_with_all_fields(self):
        """Test PrecedentCase with all optional fields"""
        precedent = PrecedentCase(
            case_ref="2022다12345",
            court="대법원",
            decision_date="2023-03-15",
            case_type="이혼",
            summary="테스트 요약",
            key_factors=["불륜", "재산분할"],
            property_division_ratio="60:40",
            alimony_amount=30000000,
            similarity_score=0.85,
            source_url="https://www.law.go.kr/..."
        )

        assert precedent.property_division_ratio == "60:40"
        assert precedent.alimony_amount == 30000000
        assert precedent.source_url is not None


class TestPrecedentSearchResponse:
    """Test suite for PrecedentSearchResponse model"""

    def test_response_model(self):
        """Test PrecedentSearchResponse model"""
        response = PrecedentSearchResponse(
            precedents=[],
            total=0,
            search_keywords=["불륜"]
        )

        assert response.precedents == []
        assert response.total == 0
        assert response.search_keywords == ["불륜"]
        assert response.warning is None

    def test_response_with_warning(self):
        """Test PrecedentSearchResponse with warning"""
        response = PrecedentSearchResponse(
            precedents=[],
            total=0,
            search_keywords=[],
            warning="Qdrant 연결 실패"
        )

        assert response.warning == "Qdrant 연결 실패"
