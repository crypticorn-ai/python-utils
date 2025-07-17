"""Defines common enumerations used throughout the codebase for type safety and consistency."""

try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum


class Exchange(StrEnum):
    """All exchanges used in the crypticorn ecosystem. Refer to the APIs for support for a specific usecase (data, trading, etc.)."""

    KUCOIN = "kucoin"
    BINGX = "bingx"
    BINANCE = "binance"
    BYBIT = "bybit"
    HYPERLIQUID = "hyperliquid"
    BITGET = "bitget"
    GATEIO = "gateio"
    BITSTAMP = "bitstamp"


class MarketType(StrEnum):
    """
    Market types
    """

    SPOT = "spot"
    FUTURES = "futures"


class ApiEnv(StrEnum):
    """The environment the API is being used with."""

    PROD = "prod"
    DEV = "dev"
    LOCAL = "local"
    DOCKER = "docker"


class BaseUrl(StrEnum):
    """The base URL to connect to the API."""

    PROD = "https://api.crypticorn.com"
    DEV = "https://api.crypticorn.dev"
    LOCAL = "http://localhost"
    DOCKER = "http://host.docker.internal"

    @classmethod
    def from_env(cls, env: ApiEnv) -> "BaseUrl":
        """Load the base URL from the API environment."""
        if env == ApiEnv.PROD:
            return cls.PROD
        elif env == ApiEnv.DEV:
            return cls.DEV
        elif env == ApiEnv.LOCAL:
            return cls.LOCAL
        elif env == ApiEnv.DOCKER:
            return cls.DOCKER
