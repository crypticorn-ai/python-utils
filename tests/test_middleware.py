from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, Request
from starlette.responses import Response

from crypticorn_utils.middleware import PrometheusMiddleware, add_middleware


class TestPrometheusMiddleware:
    """Test the PrometheusMiddleware class."""

    @pytest.fixture
    def middleware(self):
        return PrometheusMiddleware(app=MagicMock())

    @pytest.fixture
    def mock_request(self):
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.headers = {}
        request.scope = {"path": "/test"}
        request.body = AsyncMock(return_value=b"test body")
        return request

    @pytest.fixture
    def mock_response(self):
        response = MagicMock(spec=Response)
        response.status_code = 200
        response.body = AsyncMock(return_value=b"response body")
        return response

    @pytest.mark.asyncio
    async def test_dispatch_basic_request(self, middleware, mock_request, mock_response):
        """Test basic request dispatch without auth headers."""
        call_next = AsyncMock(return_value=mock_response)
        
        with patch("crypticorn_utils.middleware.HTTP_REQUESTS_COUNT") as mock_count, \
             patch("crypticorn_utils.middleware.REQUEST_SIZE") as mock_req_size, \
             patch("crypticorn_utils.middleware.RESPONSE_SIZE") as mock_resp_size, \
             patch("crypticorn_utils.middleware.HTTP_REQUEST_DURATION") as mock_duration:
            
            result = await middleware.dispatch(mock_request, call_next)
            assert result == mock_response
            call_next.assert_called_once_with(mock_request)
            mock_count.labels.assert_called_once()
            mock_req_size.labels.assert_called_once()
            mock_resp_size.labels.assert_called_once()
            mock_duration.labels.assert_called_once()

    @pytest.mark.asyncio
    async def test_auth_type_detection(self, middleware, mock_request, mock_response):
        """Test auth type detection for various auth methods."""
        test_cases = [
            ({"authorization": "Bearer token123"}, "Bearer"),
            ({"authorization": "Basic dXNlcjpwYXNz"}, "Basic"),
            ({"x-api-key": "api-key-123"}, "X-API-KEY"),
            ({"authorization": "invalidformat"}, "none"),
            ({}, "none")
        ]
        
        for headers, expected_auth_type in test_cases:
            mock_request.headers = headers
            call_next = AsyncMock(return_value=mock_response)
            with patch("crypticorn_utils.middleware.HTTP_REQUESTS_COUNT") as mock_count:
                await middleware.dispatch(mock_request, call_next)
                assert mock_count.labels.call_args[1]["auth_type"] == expected_auth_type

    @pytest.mark.asyncio
    async def test_endpoint_extraction(self, middleware, mock_request, mock_response):
        """Test endpoint extraction with route and fallback."""
        call_next = AsyncMock(return_value=mock_response)
        
        # Test with route
        mock_route = MagicMock()
        mock_route.path = "/api/v1/test"
        mock_request.scope = {"route": mock_route}
        with patch("crypticorn_utils.middleware.HTTP_REQUESTS_COUNT") as mock_count:
            await middleware.dispatch(mock_request, call_next)
            assert mock_count.labels.call_args[1]["endpoint"] == "/api/v1/test"
        
        # Test fallback to path
        mock_request.scope = {"path": "/fallback/path"}
        with patch("crypticorn_utils.middleware.HTTP_REQUESTS_COUNT") as mock_count:
            await middleware.dispatch(mock_request, call_next)
            assert mock_count.labels.call_args[1]["endpoint"] == "/fallback/path"

    @pytest.mark.asyncio
    async def test_exception_handling(self, middleware, mock_request, mock_response):
        """Test handling of body reading exceptions."""
        call_next = AsyncMock(return_value=mock_response)
        
        # Test request body exception
        mock_request.body = AsyncMock(side_effect=Exception("Body read error"))
        with patch("crypticorn_utils.middleware.REQUEST_SIZE") as mock_req_size:
            await middleware.dispatch(mock_request, call_next)
            mock_req_size.labels.assert_called_once()
        
        # Test response body exception
        mock_response.body = AsyncMock(side_effect=Exception("Response read error"))
        with patch("crypticorn_utils.middleware.RESPONSE_SIZE") as mock_resp_size:
            await middleware.dispatch(mock_request, call_next)
            mock_resp_size.labels.assert_called_once()


class TestAddMiddleware:
    """Test the add_middleware function."""

    def test_add_middleware_all_default(self):
        """Test adding all middleware by default."""
        app = FastAPI()
        
        with patch.object(app, 'add_middleware') as mock_add:
            add_middleware(app)
            
            # Should add both CORS and metrics middleware
            assert mock_add.call_count == 2

    def test_add_middleware_selective(self):
        """Test adding specific middleware types."""
        app = FastAPI()
        
        # Test CORS only
        with patch.object(app, 'add_middleware') as mock_add:
            add_middleware(app, include=["cors"])
            assert mock_add.call_count == 1
            assert "CORSMiddleware" in str(mock_add.call_args[0][0])
        
        # Test metrics only
        with patch.object(app, 'add_middleware') as mock_add:
            add_middleware(app, include=["metrics"])
            assert mock_add.call_count == 1
            assert mock_add.call_args[0][0] == PrometheusMiddleware

    def test_add_middleware_cors_configuration(self):
        """Test CORS middleware configuration."""
        app = FastAPI()
        
        with patch.object(app, 'add_middleware') as mock_add:
            add_middleware(app, include=["cors"])
            
            cors_kwargs = mock_add.call_args[1]
            assert "http://localhost:5173" in cors_kwargs["allow_origins"]
            assert "http://localhost:4173" in cors_kwargs["allow_origins"]
            assert cors_kwargs["allow_credentials"] is True
            assert cors_kwargs["allow_methods"] == ["*"]
            assert cors_kwargs["allow_headers"] == ["*"]
