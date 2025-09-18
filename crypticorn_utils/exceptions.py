import dataclasses as _dataclasses
import logging as _logging
import typing as _typing

import fastapi as _fastapi
import pydantic as _pydantic

from .types import _EXCEPTION_TYPES, _TErrorCodes

_logger = _logging.getLogger("crypticorn")


def get_exception_response(
    error_codes: _typing.TypeAlias,
) -> dict[str, dict[str, _typing.Any]]:
    """The default schema if an error is returned.
    ```python
    ErrorCodes = Literal['unknown_error', 'invalid_data_request']
    app = FastAPI(responses={**get_exception_response(ErrorCodes)})
    ```
    """
    # Note: this constructs a very ugly OpenAPI schema name for the ExceptionDetail model due to the generic type.
    # something like this: ExceptionDetailLiteralUnknownErrorInvalidDataRequestInvalidDataResponseObjectAlreadyExistsObjectNotFound...
    # Since the error codes may be extended by the server implementation, the schema name will even change.
    # Clients are advised not to use this class directly. Instead get the properties from the raw response.
    # >>> try:
    # >>>     response = requests.get(url)
    # >>>     response.json()['default']['model']
    # >>> except Exception as e:
    # >>>     # This will contain the ExceptionDetail model with the error codes as JSON
    # >>>     # instead of validating it against the schema, we can just print the error code like this:
    # >>>     print(e.get('code'))

    # This issue is tracked in Pydantic:
    # - https://docs.pydantic.dev/1.10/usage/schema/#schema-customization
    # - https://github.com/pydantic/pydantic/issues/6304
    # - https://github.com/pydantic/pydantic/issues/7376

    return {
        "default": {
            "model": _ExceptionDetail[error_codes],
            "description": "Error response",
        }
    }


class _ExceptionDetail(_pydantic.BaseModel, _typing.Generic[_TErrorCodes]):
    """Exception details returned to the client."""

    message: _typing.Optional[str] = _pydantic.Field(
        None, description="An additional error message"
    )
    code: _TErrorCodes = _pydantic.Field(..., description="The unique error code")
    status_code: int = _pydantic.Field(..., description="The HTTP status code")
    details: _typing.Any = _pydantic.Field(
        None, description="Additional details about the error"
    )

    model_config = _pydantic.ConfigDict(title="ExceptionDetail")


@_dataclasses.dataclass(frozen=True)
class BaseError(_typing.Generic[_TErrorCodes]):
    """Base API error class defining the error details.

    ```python
    class Errors:
        UNKNOWN_ERROR = BaseError[ErrorCodes](
            identifier='unknown_error',
            http_code=500,
            websocket_code=1011,
        )
    ```
    """

    identifier: _TErrorCodes
    http_code: int
    websocket_code: int

    # Class variable to store all instances
    _instances: _typing.ClassVar[dict[str, "BaseError"]] = {}

    def __post_init__(self):
        # Register this instance
        self._instances[str(self.identifier)] = self

    @classmethod
    def from_identifier(cls, identifier: _TErrorCodes) -> "BaseError[_TErrorCodes]":
        """Get an error instance by its identifier."""
        if str(identifier) not in cls._instances:
            raise ValueError(f"Unknown error identifier: {identifier}")
        return cls._instances[str(identifier)]

    @classmethod
    def get_all_instances(cls) -> dict[str, "BaseError[_TErrorCodes]"]:
        """Get all registered error instances."""
        return cls._instances.copy()


class ExceptionHandler(_typing.Generic[_TErrorCodes]):
    """This class is used to handle errors and exceptions. It is used to build exceptions and raise them.

    - Register the exception handlers to the FastAPI app.
    - Configure the instance with a callback to get the error object from the error identifier.
    - Build exceptions from error codes defined in the client code.

    Example for the client code implementation:

    ```python
    from crypticorn_utils import ExceptionHandler, BaseError
    from typing import Literal

    # Define error codes as a Literal type
    ErrorCodes = Literal[
        'unknown_error',
        'invalid_data_request',
        'invalid_data_response',
        'object_already_exists',
        'object_not_found'
    ]

    # Define errors as instances of BaseError
    class Errors:
        UNKNOWN_ERROR = BaseError[ErrorCodes](
            identifier='unknown_error',
            http_code=500,
            websocket_code=1011,
        )
        INVALID_DATA_REQUEST = BaseError[ErrorCodes](
            identifier='invalid_data_request',
            http_code=422,
            websocket_code=1007,
        )
        INVALID_DATA_RESPONSE = BaseError[ErrorCodes](
            identifier='invalid_data_response',
            http_code=422,
            websocket_code=1007,
        )
        OBJECT_ALREADY_EXISTS = BaseError[ErrorCodes](
            identifier='object_already_exists',
            http_code=409,
            websocket_code=1008,
        )
        OBJECT_NOT_FOUND = BaseError[ErrorCodes](
            identifier='object_not_found',
            http_code=404,
            websocket_code=1008,
        )

    handler = ExceptionHandler[ErrorCodes](callback=BaseError.from_identifier)
    handler.register_exception_handlers(app)

    @app.get("/")
    def get_root():
        raise handler.build_exception('object_not_found')
    ```
    """

    def __init__(
        self,
        callback: _typing.Callable[[_TErrorCodes], BaseError[_TErrorCodes]],
    ):
        """
        :param callback: The callback to use to get the error object from the error identifier.
        """
        self.callback = callback

    def _http_exception(
        self,
        content: _ExceptionDetail[_TErrorCodes],
        headers: _typing.Optional[dict[str, str]] = None,
    ) -> _fastapi.HTTPException:
        return _fastapi.HTTPException(
            detail=content.model_dump(mode="json"),
            headers=headers,
            status_code=content.status_code,
        )

    def _websocket_exception(
        self, content: _ExceptionDetail[_TErrorCodes]
    ) -> _fastapi.WebSocketException:
        return _fastapi.WebSocketException(
            reason=content.model_dump(mode="json"),
            code=content.status_code,
        )

    def build_exception(
        self,
        code: _TErrorCodes,
        *,
        message: _typing.Optional[str] = None,
        headers: _typing.Optional[dict[str, str]] = None,
        details: _typing.Any = None,
        type: _EXCEPTION_TYPES = "http",
    ) -> _typing.Union[_fastapi.HTTPException, _fastapi.WebSocketException]:
        """Build an exception, without raising it.
        :param code: The error code to raise.
        :param message: The message to include in the error.
        :param headers: The headers to include in the error.
        :param details: The details to include in the error.
        :param type: The type of exception to raise. Defaults to HTTP.

        :return: The exception to raise, either a fastapi.HTTPException or a fastapi.WebSocketException.

        ```python
        @app.get("/")
        def get_root():
            raise handler.build_exception('object_not_found')
        ```
        """
        error = self.callback(code)
        content = _ExceptionDetail[_TErrorCodes](
            message=message,
            code=error.identifier,
            status_code=error.http_code if type == "http" else error.websocket_code,
            details=details,
        )
        if type == "http":
            return self._http_exception(content, headers)
        elif type == "websocket":
            return self._websocket_exception(content)

    async def _general_handler(
        self, request: _fastapi.Request, exc: Exception
    ) -> _fastapi.responses.JSONResponse:
        """Default exception handler for all exceptions."""
        body = _ExceptionDetail[_TErrorCodes](
            message=str(exc),
            code=_typing.cast(_TErrorCodes, "unknown_error"),
            status_code=500,
        )
        res = _fastapi.responses.JSONResponse(
            status_code=body.status_code,
            content=body.model_dump(mode="json"),
            headers=None,
        )
        _logger.error(f"General error: {str(exc)}")
        return res

    async def _request_validation_handler(
        self, request: _fastapi.Request, exc: _fastapi.exceptions.RequestValidationError
    ) -> _fastapi.responses.JSONResponse:
        """Exception handler for all request validation errors."""
        body = _ExceptionDetail[_TErrorCodes](
            message=str(exc),
            code=_typing.cast(_TErrorCodes, "invalid_data_request"),
            status_code=400,
        )
        res = _fastapi.responses.JSONResponse(
            status_code=body.status_code,
            content=body.model_dump(mode="json"),
            headers=None,
        )
        _logger.error(f"Request validation error: {str(exc)}")
        return res

    async def _response_validation_handler(
        self,
        request: _fastapi.Request,
        exc: _fastapi.exceptions.ResponseValidationError,
    ) -> _fastapi.responses.JSONResponse:
        """Exception handler for all response validation errors."""
        body = _ExceptionDetail[_TErrorCodes](
            message=str(exc),
            code=_typing.cast(_TErrorCodes, "invalid_data_response"),
            status_code=400,
        )
        res = _fastapi.responses.JSONResponse(
            status_code=body.status_code,
            content=body.model_dump(mode="json"),
            headers=None,
        )
        _logger.error(f"Response validation error: {str(exc)}")
        return res

    async def _http_handler(
        self, request: _fastapi.Request, exc: _fastapi.HTTPException
    ) -> _fastapi.responses.JSONResponse:
        """Exception handler for HTTPExceptions. It unwraps the HTTPException and returns the detail in a flat JSON response."""
        res = _fastapi.responses.JSONResponse(
            status_code=exc.status_code, content=exc.detail, headers=exc.headers
        )
        _logger.error(f"HTTP error: {str(exc)}")
        return res

    def register_exception_handlers(self, app: _fastapi.FastAPI) -> None:
        """Utility to register serveral exception handlers in one go. Catches Exception, HTTPException and Data Validation errors, logs them and responds with a unified json body.

        ```python
        handler.register_exception_handlers(app)
        ```
        """
        app.add_exception_handler(Exception, self._general_handler)
        app.add_exception_handler(_fastapi.HTTPException, self._http_handler)
        app.add_exception_handler(
            _fastapi.exceptions.RequestValidationError, self._request_validation_handler
        )
        app.add_exception_handler(
            _fastapi.exceptions.ResponseValidationError,
            self._response_validation_handler,
        )
