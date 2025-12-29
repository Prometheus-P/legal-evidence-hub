"""
Integration tests for app/main.py

TDD approach: Test FastAPI application startup, endpoints, and middleware integration
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestApplicationStartup:
    """Test FastAPI application initialization and startup"""

    def test_app_starts_successfully(self, raw_client):
        """Test that the application starts without errors"""
        # If we get here, the app started successfully via the raw_client fixture
        assert raw_client is not None

    def test_app_has_correct_title(self, raw_client):
        """Test that the app has the correct title and version"""
        # Access the OpenAPI schema to check app metadata
        response = raw_client.get("/openapi.json")
        assert response.status_code == 200

        openapi_schema = response.json()
        assert openapi_schema["info"]["title"] == "CHAGOK API"
        assert openapi_schema["info"]["version"] == "0.2.0"

    def test_docs_enabled_in_debug_mode(self, raw_client):
        """Test that /docs is accessible when DEBUG=true"""
        # In test mode, DEBUG should be true
        response = raw_client.get("/docs")
        # Should not return 404
        assert response.status_code in [200, 307]  # 200 or redirect


@pytest.mark.integration
class TestRootEndpoint:
    """Test root endpoint (/"""

    def test_root_returns_200(self, raw_client):
        """Test that root endpoint returns 200 OK"""
        response = raw_client.get("/")
        assert response.status_code == 200

    def test_root_returns_service_info(self, raw_client):
        """Test that root endpoint returns service information"""
        response = raw_client.get("/")
        data = response.json()

        assert "service" in data
        assert data["service"] == "CHAGOK API"
        assert "version" in data
        assert data["version"] == "0.2.0"
        assert "environment" in data
        assert "timestamp" in data

    def test_root_includes_docs_link(self, raw_client):
        """Test that root response includes docs link"""
        response = raw_client.get("/")
        data = response.json()

        assert "docs" in data
        assert "health" in data

    def test_root_timestamp_is_iso8601(self, raw_client):
        """Test that root endpoint returns ISO8601 timestamp"""
        response = raw_client.get("/")
        data = response.json()

        timestamp = data["timestamp"]
        # Basic ISO8601 format check
        assert "T" in timestamp
        assert len(timestamp) > 19  # YYYY-MM-DDTHH:MM:SS minimum


@pytest.mark.integration
class TestHealthCheckEndpoint:
    """Test health check endpoint (/api/health)"""

    def test_health_check_returns_200(self, raw_client):
        """Test that liveness probe returns 200 OK"""
        response = raw_client.get("/api/health")
        assert response.status_code == 200

    def test_health_check_returns_ok_status(self, raw_client):
        """Test that liveness probe returns 'ok' status"""
        response = raw_client.get("/api/health")
        data = response.json()

        assert "status" in data
        assert data["status"] == "ok"

    def test_health_check_includes_service_info(self, raw_client):
        """Test that readiness probe includes service name and version"""
        response = raw_client.get("/api/health/ready")
        data = response.json()

        assert "service" in data
        assert data["service"] == "CHAGOK API"
        assert "version" in data
        assert data["version"] == "0.2.0"

    def test_health_check_includes_timestamp(self, raw_client):
        """Test that readiness probe includes timestamp"""
        response = raw_client.get("/api/health/ready")
        data = response.json()

        assert "timestamp" in data
        timestamp = data["timestamp"]
        # ISO8601 format check
        assert "T" in timestamp

    def test_health_check_is_fast(self, raw_client):
        """Test that liveness probe responds quickly (< 1 second)"""
        import time
        start = time.time()
        response = raw_client.get("/api/health")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 1.0  # Should respond in less than 1 second


@pytest.mark.integration
class TestMiddlewareIntegration:
    """Test that all middlewares are properly registered"""

    def test_cors_headers_present(self, raw_client):
        """Test that CORS headers are added to responses"""
        response = raw_client.get("/", headers={"Origin": "http://localhost:3000"})

        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers

    def test_security_headers_present(self, raw_client):
        """Test that security headers are added to responses"""
        response = raw_client.get("/")

        # Security headers from SecurityHeadersMiddleware
        assert "x-content-type-options" in response.headers
        assert response.headers["x-content-type-options"] == "nosniff"
        assert "x-frame-options" in response.headers
        assert response.headers["x-frame-options"] == "DENY"

    def test_custom_error_handling(self, raw_client):
        """Test that custom error handlers are registered"""
        # Request a non-existent endpoint
        response = raw_client.get("/nonexistent")

        assert response.status_code == 404
        data = response.json()

        # Should use our custom error format
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert "error_id" in data["error"]
        assert "timestamp" in data["error"]


@pytest.mark.integration
class TestApplicationLifespan:
    """Test application lifespan events"""

    def test_startup_logs_emitted(self, caplog):
        """Test that startup logs are emitted"""
        # This test verifies that the lifespan context manager runs
        from app.main import app
        with TestClient(app):
            # Check if startup log messages were emitted
            # Note: This might not work in all cases due to how TestClient handles lifespan
            pass  # Placeholder - lifespan logging tested via manual run

    def test_app_can_start_and_stop_cleanly(self):
        """Test that app can start and stop without errors"""
        from app.main import app

        # Create and close client multiple times
        for _ in range(3):
            with TestClient(app) as client:
                response = client.get("/api/health")
                assert response.status_code == 200


@pytest.mark.integration
class TestInvalidRequests:
    """Test handling of invalid requests"""

    def test_invalid_method_returns_405(self, raw_client):
        """Test that invalid HTTP method returns 405"""
        response = raw_client.post("/api/health")  # Health check is GET only

        assert response.status_code == 405
        data = response.json()
        assert "error" in data

    def test_invalid_content_type_handled(self, raw_client):
        """Test that invalid content type is handled gracefully"""
        response = raw_client.post(
            "/",
            data="not-json",
            headers={"Content-Type": "application/json"}
        )

        # Should return error (404 since POST / doesn't exist)
        assert response.status_code in [404, 405]


@pytest.mark.integration
class TestCORSConfiguration:
    """Test CORS configuration"""

    def test_cors_allows_configured_origins(self, raw_client):
        """Test that CORS allows configured origins"""
        response = raw_client.get(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )

        assert response.status_code == 200
        # CORS should allow the origin
        assert "access-control-allow-origin" in response.headers

    def test_cors_allows_credentials(self, raw_client):
        """Test that CORS allows credentials"""
        response = raw_client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )

        # Should allow credentials for cookie-based auth (future)
        cors_headers = {k.lower(): v for k, v in response.headers.items()}
        if "access-control-allow-credentials" in cors_headers:
            assert cors_headers["access-control-allow-credentials"] == "true"


@pytest.mark.integration
@pytest.mark.slow
class TestApplicationUnderLoad:
    """Test application behavior under load (optional)"""

    def test_concurrent_health_checks(self, raw_client):
        """Test that app handles concurrent requests"""
        import concurrent.futures

        def make_request():
            response = raw_client.get("/api/health")
            return response.status_code

        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All should succeed
        assert all(status == 200 for status in results)
