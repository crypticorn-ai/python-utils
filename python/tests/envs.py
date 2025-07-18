import asyncio
import os
from dotenv import load_dotenv
from crypticorn_utils.enums import BaseUrl, Scope
from crypticorn_utils.utils import gen_random_id
from crypticorn import AsyncClient
from crypticorn.auth import CreateApiKeyRequest
import jwt
import time
import datetime

load_dotenv()


async def generate_valid_jwt(
    user_id: str, scopes: list[Scope] = [], is_admin=False, expires_at: int = None
):
    now = int(time.time())
    payload = {
        "sub": user_id,
        "aud": JWT_AUDIENCE,
        "iss": JWT_ISSUER,
        "jti": gen_random_id(),
        "iat": now,
        "exp": expires_at or now + JWT_EXPIRES_IN,
        "scopes": scopes,
        "admin": is_admin,
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token


async def generate_api_key(
    user_id: str, scopes: list[Scope] = [], expires_at: datetime.datetime = None
):
    async with AsyncClient(
        base_url=BaseUrl.from_env(API_ENV),
        jwt=await generate_valid_jwt(user_id=user_id, scopes=scopes),
    ) as api_client:
        res = await api_client.auth.login.create_api_key(
            CreateApiKeyRequest(
                name=f"pytest-{gen_random_id()}",
                scopes=scopes,
                expires_at=expires_at,
            )
        )
        return res.api_key


API_ENV = os.getenv("API_ENV")
if not API_ENV:
    raise ValueError("API_ENV is not set")

# JWT
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise ValueError("JWT_SECRET is not set")
JWT_ISSUER = os.getenv("JWT_ISSUER")
if not JWT_ISSUER:
    raise ValueError("JWT_ISSUER is not set")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE")
if not JWT_AUDIENCE:
    raise ValueError("JWT_AUDIENCE is not set")
JWT_EXPIRES_IN = 60 * 60  # 1 hour
USER_ID = os.getenv("USER_ID")
if not USER_ID:
    raise ValueError("USER_ID is not set")
EXPIRED_JWT = asyncio.run(
    generate_valid_jwt(
        user_id=USER_ID, expires_at=datetime.datetime.now() - datetime.timedelta(days=1)
    )
)
VALID_JWT = asyncio.run(
    generate_valid_jwt(user_id="user-without-read-predictions")
)  # dummy user since the USER_ID has access to the predictions ($300+)
VALID_PREDICTION_JWT = asyncio.run(
    generate_valid_jwt(user_id="user-with-read-predictions", scopes=['read:predictions'])
)
VALID_ADMIN_JWT = asyncio.run(
    generate_valid_jwt(
        user_id=USER_ID, scopes=Scope.purchaseable_scopes(), is_admin=True
    )
)
# API KEY
ONE_SCOPE_API_KEY_SCOPE = Scope.READ_TRADE_BOTS
ONE_SCOPE_API_KEY = asyncio.run(
    generate_api_key(
        user_id=USER_ID,
        scopes=[ONE_SCOPE_API_KEY_SCOPE],
        expires_at=datetime.datetime.now() + datetime.timedelta(days=1),  # 1 day
    )
)
EXPIRED_API_KEY = asyncio.run(
    generate_api_key(
        user_id=USER_ID,
        scopes=[ONE_SCOPE_API_KEY_SCOPE],
        expires_at=datetime.datetime.now() - datetime.timedelta(days=1),  # 1 day ago
    )
)

if not VALID_JWT:
    raise ValueError("VALID_JWT is not set")
if not EXPIRED_JWT:
    raise ValueError("EXPIRED_JWT is not set")
if not ONE_SCOPE_API_KEY:
    raise ValueError("ONE_SCOPE_API_KEY is not set")
if not EXPIRED_API_KEY:
    raise ValueError("EXPIRED_API_KEY is not set")
