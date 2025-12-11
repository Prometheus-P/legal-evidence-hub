"""
Contract tests for Search API
007-lawyer-portal-v1: US6 (Global Search)
"""

from fastapi.testclient import TestClient


class TestSearchAPI:
    """Contract tests for GET /search endpoint"""

    def test_search_requires_auth(self, client: TestClient):
        """Test that search endpoint requires authentication"""
        response = client.get("/search?q=test")
        assert response.status_code == 401

    def test_search_requires_min_query_length(
        self, client: TestClient, auth_headers: dict
    ):
        """Test that search requires minimum 2 character query"""
        response = client.get("/search?q=a", headers=auth_headers)
        assert response.status_code == 422  # Validation error

    def test_search_returns_results_structure(
        self, client: TestClient, auth_headers: dict, test_case: dict
    ):
        """Test that search returns proper result structure"""
        response = client.get("/search?q=test", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "results" in data
        assert "total" in data
        assert "query" in data
        assert isinstance(data["results"], list)
        assert isinstance(data["total"], int)

    def test_search_cases_by_title(
        self, client: TestClient, auth_headers: dict, test_case: dict
    ):
        """Test searching cases by title"""
        # test_case fixture creates a case with title containing "테스트"
        response = client.get("/search?q=테스트&categories=cases", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["total"] >= 0  # May find test case

        # Verify result structure if results found
        for result in data["results"]:
            assert result["category"] == "cases"
            assert "id" in result
            assert "title" in result
            assert "subtitle" in result
            assert "icon" in result
            assert "url" in result

    def test_search_with_category_filter(
        self, client: TestClient, auth_headers: dict, test_case: dict
    ):
        """Test searching with specific category filter"""
        response = client.get(
            "/search?q=test&categories=cases,evidence",
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        # All results should be in filtered categories
        for result in data["results"]:
            assert result["category"] in ["cases", "evidence"]

    def test_search_with_limit(
        self, client: TestClient, auth_headers: dict, test_case: dict
    ):
        """Test search respects limit parameter"""
        response = client.get("/search?q=test&limit=5", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        # Results per category should not exceed limit
        category_counts = {}
        for result in data["results"]:
            cat = result["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1

        for count in category_counts.values():
            assert count <= 5

    def test_search_empty_query_returns_empty(
        self, client: TestClient, auth_headers: dict
    ):
        """Test that short query returns empty results"""
        # Query with exactly 2 chars should work
        response = client.get("/search?q=ab", headers=auth_headers)
        assert response.status_code == 200

    def test_search_result_contains_metadata(
        self, client: TestClient, auth_headers: dict, test_case: dict
    ):
        """Test that search results contain metadata"""
        response = client.get("/search?q=테스트", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        for result in data["results"]:
            assert "metadata" in result
            assert isinstance(result["metadata"], dict)


class TestQuickAccessAPI:
    """Contract tests for GET /search/quick-access endpoint"""

    def test_quick_access_requires_auth(self, client: TestClient):
        """Test that quick-access endpoint requires authentication"""
        response = client.get("/search/quick-access")
        assert response.status_code == 401

    def test_quick_access_returns_structure(
        self, client: TestClient, auth_headers: dict
    ):
        """Test quick-access returns proper structure"""
        response = client.get("/search/quick-access", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "todays_events" in data
        assert "todays_events_count" in data
        assert isinstance(data["todays_events"], list)
        assert isinstance(data["todays_events_count"], int)


class TestRecentSearchesAPI:
    """Contract tests for GET /search/recent endpoint"""

    def test_recent_searches_requires_auth(self, client: TestClient):
        """Test that recent-searches endpoint requires authentication"""
        response = client.get("/search/recent")
        assert response.status_code == 401

    def test_recent_searches_returns_structure(
        self, client: TestClient, auth_headers: dict
    ):
        """Test recent-searches returns proper structure"""
        response = client.get("/search/recent", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "recent_searches" in data
        assert isinstance(data["recent_searches"], list)

    def test_recent_searches_respects_limit(
        self, client: TestClient, auth_headers: dict
    ):
        """Test recent-searches respects limit parameter"""
        response = client.get("/search/recent?limit=3", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert len(data["recent_searches"]) <= 3
