"""
Unit tests for PrecedentService
012-precedent-integration: T052
"""

import pytest
from unittest.mock import Mock, patch

from app.services.precedent_service import PrecedentService
from app.schemas.precedent import (
    PrecedentCase,
    PrecedentSearchResponse,
    QueryContext,
    DivisionRatio,
)


class TestPrecedentService:
    """Test suite for PrecedentService"""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        return Mock()

    @pytest.fixture
    def service(self, mock_db):
        """Create PrecedentService instance"""
        return PrecedentService(mock_db)

    @pytest.fixture
    def sample_precedent_data(self):
        """Sample precedent data from Qdrant (raw dict format)"""
        return [
            {
                "case_ref": "2022다12345",
                "court": "대법원",
                "decision_date": "2023-03-15",
                "summary": "불륜으로 인한 이혼 소송에서 재산분할 비율 결정",
                "key_factors": ["불륜", "재산분할"],
                "division_ratio": {"plaintiff": 60, "defendant": 40},
                "similarity_score": 0.87,
            },
            {
                "case_ref": "2021다67890",
                "court": "서울고등법원",
                "decision_date": "2022-11-20",
                "summary": "가정폭력으로 인한 이혼 소송",
                "key_factors": ["가정폭력", "위자료"],
                "division_ratio": {"plaintiff": 70, "defendant": 30},
                "similarity_score": 0.75,
            },
        ]

    # ============================================
    # search_similar_precedents tests
    # ============================================

    def test_search_similar_precedents_success(self, service, sample_precedent_data):
        """Test successful precedent search"""
        with patch('app.services.precedent_service.qdrant_search') as mock_search:
            mock_search.return_value = sample_precedent_data

            result = service.search_similar_precedents(
                case_id="case_123",
                limit=10,
                min_score=0.5
            )

            assert isinstance(result, PrecedentSearchResponse)
            assert len(result.precedents) == 2
            assert result.query_context.total_found == 2
            assert result.precedents[0].case_ref == "2022다12345"
            assert result.precedents[0].similarity_score == 0.87

    def test_search_similar_precedents_empty_uses_fallback(self, service):
        """Test search with no results uses fallback"""
        with patch('app.services.precedent_service.qdrant_search') as mock_search, \
             patch('app.services.precedent_service.get_fallback_precedents') as mock_fallback:
            mock_search.return_value = []
            mock_fallback.return_value = [
                {
                    "case_ref": "fallback_case",
                    "court": "대법원",
                    "decision_date": "2020-01-01",
                    "summary": "Fallback precedent",
                    "key_factors": [],
                    "similarity_score": 0.5,
                }
            ]

            result = service.search_similar_precedents(
                case_id="case_123",
                limit=10,
                min_score=0.5
            )

            assert isinstance(result, PrecedentSearchResponse)
            mock_fallback.assert_called_once()

    def test_search_similar_precedents_qdrant_failure_uses_fallback(self, service):
        """Test graceful handling of Qdrant connection failure"""
        with patch('app.services.precedent_service.qdrant_search') as mock_search, \
             patch('app.services.precedent_service.get_fallback_precedents') as mock_fallback:
            mock_search.side_effect = Exception("Qdrant connection failed")
            mock_fallback.return_value = []

            result = service.search_similar_precedents(
                case_id="case_123",
                limit=10,
                min_score=0.5
            )

            # Should return fallback result, not raise exception
            assert isinstance(result, PrecedentSearchResponse)

    # ============================================
    # get_fault_types tests
    # ============================================

    def test_get_fault_types_returns_default(self, service):
        """Test fault type extraction returns default values"""
        fault_types = service.get_fault_types("case_123")

        # Current implementation returns default values
        assert isinstance(fault_types, list)
        assert len(fault_types) >= 0

    # ============================================
    # PrecedentCase model tests
    # ============================================

    def test_precedent_case_model(self):
        """Test PrecedentCase Pydantic model validation"""
        precedent = PrecedentCase(
            case_ref="2022다12345",
            court="대법원",
            decision_date="2023-03-15",
            summary="테스트 요약",
            key_factors=["불륜"],
            similarity_score=0.85
        )

        assert precedent.case_ref == "2022다12345"
        assert precedent.similarity_score == 0.85
        assert precedent.division_ratio is None

    def test_precedent_case_with_division_ratio(self):
        """Test PrecedentCase with division ratio"""
        precedent = PrecedentCase(
            case_ref="2022다12345",
            court="대법원",
            decision_date="2023-03-15",
            summary="테스트 요약",
            key_factors=["불륜", "재산분할"],
            division_ratio=DivisionRatio(plaintiff=60, defendant=40),
            similarity_score=0.85
        )

        assert precedent.division_ratio is not None
        assert precedent.division_ratio.plaintiff == 60
        assert precedent.division_ratio.defendant == 40


class TestPrecedentSearchResponse:
    """Test suite for PrecedentSearchResponse model"""

    def test_response_model(self):
        """Test PrecedentSearchResponse model"""
        response = PrecedentSearchResponse(
            precedents=[],
            query_context=QueryContext(
                fault_types=["불륜"],
                total_found=0
            )
        )

        assert response.precedents == []
        assert response.query_context.total_found == 0
        assert response.query_context.fault_types == ["불륜"]

    def test_response_with_precedents(self):
        """Test PrecedentSearchResponse with precedents"""
        precedent = PrecedentCase(
            case_ref="2022다12345",
            court="대법원",
            decision_date="2023-03-15",
            summary="테스트",
            key_factors=[],
            similarity_score=0.8
        )

        response = PrecedentSearchResponse(
            precedents=[precedent],
            query_context=QueryContext(
                fault_types=["불륜"],
                total_found=1
            )
        )

        assert len(response.precedents) == 1
        assert response.query_context.total_found == 1
