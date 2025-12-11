"""
Unit tests for Search Service
009-mvp-gap-closure: US4 - CI 테스트 커버리지 정상화
"""

from unittest.mock import MagicMock

from app.services.search_service import SearchService, SearchResult


class TestSearchResult:
    """Unit tests for SearchResult class"""

    def test_search_result_init_default_values(self):
        """Test SearchResult with default values"""
        result = SearchResult(
            category="cases",
            id="case-123",
            title="테스트 케이스"
        )

        assert result.category == "cases"
        assert result.id == "case-123"
        assert result.title == "테스트 케이스"
        assert result.subtitle is None
        assert result.icon == ""
        assert result.url is None
        assert result.metadata == {}

    def test_search_result_init_all_values(self):
        """Test SearchResult with all values"""
        result = SearchResult(
            category="evidence",
            id="ev-123",
            title="증거파일.pdf",
            subtitle="테스트 설명",
            icon="paperclip",
            url="/cases/case-123/evidence/ev-123",
            metadata={"case_id": "case-123", "file_type": "pdf"}
        )

        assert result.category == "evidence"
        assert result.subtitle == "테스트 설명"
        assert result.icon == "paperclip"
        assert result.url == "/cases/case-123/evidence/ev-123"
        assert result.metadata == {"case_id": "case-123", "file_type": "pdf"}

    def test_search_result_to_dict(self):
        """Test SearchResult.to_dict() method"""
        result = SearchResult(
            category="cases",
            id="case-123",
            title="테스트 케이스",
            subtitle="이혼 소송",
            icon="folder",
            url="/cases/case-123",
            metadata={"status": "active"}
        )

        dict_result = result.to_dict()

        assert dict_result == {
            "category": "cases",
            "id": "case-123",
            "title": "테스트 케이스",
            "subtitle": "이혼 소송",
            "icon": "folder",
            "url": "/cases/case-123",
            "metadata": {"status": "active"}
        }


class TestSearchServiceInit:
    """Unit tests for SearchService initialization"""

    def test_init_stores_db(self):
        """Test SearchService stores db session"""
        mock_db = MagicMock()

        service = SearchService(mock_db)

        assert service.db == mock_db


class TestSearchServiceSearch:
    """Unit tests for SearchService.search() method"""

    def test_search_empty_query_returns_empty(self):
        """Returns empty results for empty query (line 81)"""
        mock_db = MagicMock()
        service = SearchService(mock_db)

        result = service.search("", "user-123")

        assert result == {"results": [], "total": 0}

    def test_search_short_query_returns_empty(self):
        """Returns empty results for query < 2 chars (line 81)"""
        mock_db = MagicMock()
        service = SearchService(mock_db)

        result = service.search("a", "user-123")

        assert result == {"results": [], "total": 0}

    def test_search_whitespace_query_returns_empty(self):
        """Returns empty results for whitespace-only query (line 81)"""
        mock_db = MagicMock()
        service = SearchService(mock_db)

        result = service.search("   ", "user-123")

        assert result == {"results": [], "total": 0}

    def test_search_none_query_returns_empty(self):
        """Returns empty results for None query (line 81)"""
        mock_db = MagicMock()
        service = SearchService(mock_db)

        result = service.search(None, "user-123")

        assert result == {"results": [], "total": 0}


class TestSearchServiceGetRecentSearches:
    """Unit tests for SearchService.get_recent_searches() method"""

    def test_get_recent_searches_returns_list(self):
        """Returns list of recent searches"""
        mock_db = MagicMock()
        service = SearchService(mock_db)

        result = service.get_recent_searches("user-123")

        assert isinstance(result, list)

    def test_get_recent_searches_with_limit(self):
        """Respects limit parameter"""
        mock_db = MagicMock()
        service = SearchService(mock_db)

        result = service.get_recent_searches("user-123", limit=5)

        assert isinstance(result, list)
        assert len(result) <= 5
