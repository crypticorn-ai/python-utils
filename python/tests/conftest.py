import httpx
import pytest
import pytest_asyncio
from crypticorn_utils.auth import AuthHandler
from crypticorn_utils.enums import BaseUrl
from crypticorn_utils.router.status_router import router as status_router
from crypticorn_utils.router.admin_router import router as admin_router
from fastapi import FastAPI
from typing import AsyncGenerator
from tests.envs import API_ENV


@pytest_asyncio.fixture()
async def auth_handler() -> AsyncGenerator[AuthHandler, None]:
    handler = AuthHandler(BaseUrl.from_env(API_ENV))
    assert BaseUrl.from_env(API_ENV) in handler.url
    yield handler
    await handler.client.base_client.close()


@pytest.fixture(scope="session")
def app():
    """
    FastAPI application instance for integration testing.
    Includes common routers (status and admin) that are available in the current codebase.
    """
    app = FastAPI()
    app.include_router(status_router)
    app.include_router(admin_router)
    return app


@pytest.fixture(scope="session")
def mock_auth_headers():
    """
    Mock authentication headers for testing protected endpoints.
    """
    return {
        "Authorization": "Bearer mock-token",
        "X-API-Key": "mock-api-key",
        "X-Refresh-Token": "mock-refresh-token",
    }


# Service client fixtures for HTTP testing
@pytest.fixture(scope="session")
def client_sync(app):
    """Synchronous HTTP client for testing endpoints."""
    return httpx.Client(app=app, base_url="http://testserver")


@pytest_asyncio.fixture
async def client(app):
    """
    HTTPX AsyncClient fixture bound to the FastAPI test app.
    """
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client
