from crypticorn.common import (
    AuthHandler as AuthHandler,
    Scope as Scope,
    Verify200Response as Verify200Response,
    BaseUrl as BaseUrl,
    ApiEnv as ApiEnv,
)
from fastapi import Security as Security
import os
import dotenv
import logging

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

DOCKER_ENV = os.getenv("IS_DOCKER", "0")
API_ENV = os.getenv("API_ENV")

if not API_ENV:
    raise ValueError(
        "API_ENV is not set. Please set it to 'prod', 'dev' or 'local' in .env (of type ApiEnv)."
    )

if DOCKER_ENV == "0":
    logger.info(f"Using {API_ENV} environment")
    base_url = BaseUrl.from_env(ApiEnv(API_ENV))
else:
    base_url = BaseUrl.DOCKER
    logger.info("Using docker environment")

auth_handler = AuthHandler(base_url=base_url)
logger.info(f"Auth URL: {auth_handler.client.config.host}")
