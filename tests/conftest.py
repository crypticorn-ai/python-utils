from typing import AsyncGenerator, cast

import pytest_asyncio

from crypticorn_utils.auth import AuthHandler
from crypticorn_utils.types import ApiEnv, BaseUrl

from .envs import API_ENV


@pytest_asyncio.fixture(scope="function")
async def auth_handler() -> AsyncGenerator[AuthHandler, None]:
    """Create a fresh AuthHandler instance for each test to ensure complete isolation."""
    handler = AuthHandler(BaseUrl.from_env(cast(ApiEnv, API_ENV)))
    assert BaseUrl.from_env(cast(ApiEnv, API_ENV)) in handler.url
    yield handler
    await handler.client.base_client.close()
