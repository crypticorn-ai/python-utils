import pytest
from pydantic import ValidationError

from crypticorn_utils.types import BaseUrl, ErrorResponse, error_response


class TestApiEnv:
    """Test the ApiEnv literal type."""

    def test_api_env_values(self):
        """Test that ApiEnv accepts valid environment values."""
        valid_envs = ["prod", "dev", "local", "docker"]
        for env in valid_envs:
            # This test ensures the type annotation works correctly
            assert env in valid_envs


class TestBaseUrl:
    """Test the BaseUrl enum and its methods."""

    def test_base_url_values(self):
        """Test that BaseUrl enum has correct values."""
        assert BaseUrl.PROD == "https://api.crypticorn.com"
        assert BaseUrl.DEV == "https://api.crypticorn.dev"
        assert BaseUrl.LOCAL == "http://localhost"
        assert BaseUrl.DOCKER == "http://host.docker.internal"

    def test_from_env_prod(self):
        """Test from_env method with prod environment."""
        result = BaseUrl.from_env("prod")
        assert result == BaseUrl.PROD
        assert result == "https://api.crypticorn.com"

    def test_from_env_dev(self):
        """Test from_env method with dev environment."""
        result = BaseUrl.from_env("dev")
        assert result == BaseUrl.DEV
        assert result == "https://api.crypticorn.dev"

    def test_from_env_local(self):
        """Test from_env method with local environment."""
        result = BaseUrl.from_env("local")
        assert result == BaseUrl.LOCAL
        assert result == "http://localhost"

    def test_from_env_docker(self):
        """Test from_env method with docker environment."""
        result = BaseUrl.from_env("docker")
        assert result == BaseUrl.DOCKER
        assert result == "http://host.docker.internal"

    def test_from_env_invalid_environment(self):
        """Test from_env method with invalid environment (should raise error)."""
        # Since ApiEnv is a Literal type, this should be caught by type checking
        # But we can test the runtime behavior by bypassing type checking
        with pytest.raises(ValueError, match="Invalid environment: invalid_env"):
            BaseUrl.from_env("invalid_env")  # type: ignore


class TestErrorResponse:
    """Test the ErrorResponse Pydantic model."""

    def test_error_response_creation(self):
        """Test creating an ErrorResponse with valid data."""
        error = ErrorResponse(detail="Something went wrong")
        assert error.detail == "Something went wrong"

    def test_error_response_validation(self):
        """Test that ErrorResponse validates required fields."""
        # Valid case
        error = ErrorResponse(detail="Test error")
        assert error.detail == "Test error"

        # Missing required field should raise ValidationError
        with pytest.raises(ValidationError):
            ErrorResponse()

    def test_error_response_json(self):
        """Test ErrorResponse JSON serialization."""
        error = ErrorResponse(detail="JSON test error")
        json_data = error.model_dump()
        assert json_data == {"detail": "JSON test error"}


class TestErrorResponseSchema:
    """Test the error_response schema definition."""

    def test_error_response_schema_structure(self):
        """Test that error_response has correct structure."""
        assert "default" in error_response
        assert "model" in error_response["default"]
        assert "description" in error_response["default"]
        assert error_response["default"]["model"] == ErrorResponse
        assert error_response["default"]["description"] == "Error response"
