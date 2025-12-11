"""
Unit tests for Latency Logging Middleware
"""

from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.latency import (
    LatencyLoggingMiddleware,
    SLOW_REQUEST_THRESHOLD,
    get_latency_middleware
)


class TestLatencyLoggingMiddleware:
    """Unit tests for LatencyLoggingMiddleware"""

    def test_adds_response_time_header(self):
        """Response includes X-Response-Time header"""
        app = FastAPI()
        app.add_middleware(LatencyLoggingMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 200
        assert "X-Response-Time" in response.headers
        assert "ms" in response.headers["X-Response-Time"]

    def test_response_time_is_numeric(self):
        """X-Response-Time header contains valid numeric value"""
        app = FastAPI()
        app.add_middleware(LatencyLoggingMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)
        response = client.get("/test")

        time_str = response.headers["X-Response-Time"]
        time_value = float(time_str.replace("ms", ""))
        assert time_value >= 0

    def test_logs_normal_request(self):
        """Normal requests are logged at INFO level"""
        app = FastAPI()
        app.add_middleware(LatencyLoggingMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)

        with patch("app.middleware.latency.logger") as mock_logger:
            response = client.get("/test")

            assert response.status_code == 200
            mock_logger.info.assert_called()
            # Verify log message contains API_LATENCY
            call_args = mock_logger.info.call_args[0][0]
            assert "API_LATENCY" in call_args

    def test_logs_slow_request_as_warning(self):
        """Slow requests (>1s) are logged at WARNING level"""
        import time

        app = FastAPI()
        app.add_middleware(LatencyLoggingMiddleware)

        @app.get("/slow")
        async def slow_endpoint():
            time.sleep(1.1)  # Exceed threshold
            return {"status": "ok"}

        client = TestClient(app)

        with patch("app.middleware.latency.logger") as mock_logger:
            response = client.get("/slow")

            assert response.status_code == 200
            mock_logger.warning.assert_called()
            # Verify log message contains SLOW_REQUEST
            call_args = mock_logger.warning.call_args[0][0]
            assert "SLOW_REQUEST" in call_args

    def test_slow_request_threshold_constant(self):
        """SLOW_REQUEST_THRESHOLD is 1.0 second"""
        assert SLOW_REQUEST_THRESHOLD == 1.0

    def test_logs_method_and_path(self):
        """Log includes HTTP method and path"""
        app = FastAPI()
        app.add_middleware(LatencyLoggingMiddleware)

        @app.post("/api/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)

        with patch("app.middleware.latency.logger") as mock_logger:
            response = client.post("/api/test")

            assert response.status_code == 200
            call_args = mock_logger.info.call_args[0][0]
            assert "POST" in call_args
            assert "/api/test" in call_args

    def test_logs_include_latency_data_extra(self):
        """Log includes latency_data in extra parameter"""
        app = FastAPI()
        app.add_middleware(LatencyLoggingMiddleware)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)

        with patch("app.middleware.latency.logger") as mock_logger:
            response = client.get("/test")

            assert response.status_code == 200
            # Check extra parameter contains latency_data
            call_kwargs = mock_logger.info.call_args[1]
            assert "extra" in call_kwargs
            assert "latency_data" in call_kwargs["extra"]

            latency_data = call_kwargs["extra"]["latency_data"]
            assert "method" in latency_data
            assert "path" in latency_data
            assert "status_code" in latency_data
            assert "latency_ms" in latency_data
            assert "slow" in latency_data

    def test_handles_error_responses(self):
        """Middleware handles error responses correctly"""
        from fastapi import HTTPException

        app = FastAPI()
        app.add_middleware(LatencyLoggingMiddleware)

        @app.get("/error")
        async def error_endpoint():
            raise HTTPException(status_code=400, detail="Test error")

        client = TestClient(app)

        with patch("app.middleware.latency.logger") as mock_logger:
            response = client.get("/error")

            assert response.status_code == 400
            # Should still log the request (either info or warning)
            assert mock_logger.info.called or mock_logger.warning.called

    def test_get_latency_middleware_returns_class(self):
        """get_latency_middleware factory returns middleware class"""
        middleware_class = get_latency_middleware()
        assert middleware_class is LatencyLoggingMiddleware


class TestLatencyMiddlewareIntegration:
    """Integration tests with the main app"""

    def test_middleware_registered_in_app(self, client):
        """Middleware is properly registered in the app"""
        response = client.get("/health")

        assert response.status_code == 200
        assert "X-Response-Time" in response.headers

    def test_latency_header_on_all_endpoints(self, client, auth_headers):
        """All endpoints include latency header"""
        endpoints = [
            ("/", "GET"),
            ("/health", "GET"),
        ]

        for path, method in endpoints:
            if method == "GET":
                response = client.get(path)
            else:
                response = client.post(path)

            assert "X-Response-Time" in response.headers, f"Missing header for {method} {path}"
