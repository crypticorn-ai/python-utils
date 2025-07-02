import logging
from typing import Any, Callable, Optional, TypedDict, Union

from crypticorn_utils.errors import (
    ApiErrorLevel,
    ApiErrorType,
)
from fastapi import FastAPI, HTTPException, WebSocketException
from fastapi import HTTPException as FastAPIHTTPException
from fastapi import Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum

_logger = logging.getLogger("crypticorn")

TError = TypedDict(
    "TError",
    {
        "identifier": str,
        "type": ApiErrorType,
        "level": ApiErrorLevel,
        "http_code": int,
        "websocket_code": int,
    }
)

class ExceptionType(StrEnum):
    """The protocol the exception is called from"""

    HTTP = "http"
    WEBSOCKET = "websocket"


class ExceptionDetail(BaseModel):
    """Exception details returned to the client."""

    message: Optional[str] = Field(None, description="An additional error message")
    code: str = Field(..., description="The unique error code")
    type: ApiErrorType = Field(..., description="The type of error")
    level: ApiErrorLevel = Field(..., description="The level of the error")
    status_code: int = Field(..., description="The HTTP status code")
    details: Any = Field(None, description="Additional details about the error")

    
class ExceptionHandler:
    """This class is used to handle errors and exceptions. It is used to build exceptions and raise them.

    - Register the exception handlers to the FastAPI app.
    - Configure the instance with a callback to get the error object from the error identifier.
    - Build exceptions from error codes defined in the client code.

    Example for the client code implementation:

    ```python
    from crypticorn_utils import ExceptionHandler, ApiErrorType, ApiErrorLevel, TError

    handler = ExceptionHandler(callback=ApiError.from_identifier)
    handler.register_exception_handlers(app)

    @app.get("/")
    def get_root():
        raise handler.build_exception(ApiErrorIdentifier.UNKNOWN_ERROR)
    
    class ApiErrorIdentifier(StrEnum):
        UNKNOWN_ERROR = "unknown_error"
        
    # Must implement the TError interface.
    class ApiError(Enum):

        UNKNOWN_ERROR = (
            ApiErrorIdentifier.UNKNOWN_ERROR,
            ApiErrorType.SERVER_ERROR,
            ApiErrorLevel.ERROR,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            status.WS_1011_INTERNAL_ERROR,
        )
        @property
        def identifier(self) -> str:
            return self.value[0]

        @property
        def type(self) -> ApiErrorType:
            return self.value[1]

        @property
        def level(self) -> ApiErrorLevel:
            return self.value[2]

        @property
        def http_code(self) -> int:
            return self.value[3]

        @property
        def websocket_code(self) -> int:
            return self.value[4]

        @classmethod
        def from_identifier(cls, identifier: str) -> Self:
            return next(error for error in cls if error.identifier == identifier)
    ```
    """
    
    def __init__(
        self, 
        callback: Callable[[str], TError],
        type: Optional[ExceptionType] = ExceptionType.HTTP,
    ):
        """
        :param callback: The callback to use to get the error object from the error identifier.
        :param type: The type of exception to raise. Defaults to HTTP.
        """
        self.callback = callback
        self.type = type

    def _http_exception(self, content: ExceptionDetail, headers: Optional[dict[str, str]] = None) -> HTTPException:
        return HTTPException(
            detail=content.model_dump(mode="json"),
            headers=headers,
            status_code=content.status_code,
        )
    
    def _websocket_exception(self, content: ExceptionDetail) -> WebSocketException:
        return WebSocketException(
            reason=content.model_dump(mode="json"),
            code=content.status_code,
        )
    
    def build_exception(
        self,
        code: str,
        message: Optional[str] = None,
        headers: Optional[dict[str, str]] = None,
        details: Any = None,
    ) -> Union[HTTPException, WebSocketException]:
        """Build an exception, without raising it.
        :param code: The error code to raise.
        :param message: The message to include in the error.
        :param headers: The headers to include in the error.
        :param details: The details to include in the error.

        :return: The exception to raise, either an HTTPException or a WebSocketException.

        ```python
        @app.get("/")
        def get_root():
            raise handler.build_exception(ApiErrorIdentifier.UNKNOWN_ERROR)
        ```
        """
        error = self.callback(code)
        content = ExceptionDetail(message=message, code=error.identifier, type=error.type, level=error.level, status_code=error.http_code, details=details)
        if self.type == ExceptionType.HTTP:
            return self._http_exception(content, headers)
        elif self.type == ExceptionType.WEBSOCKET:
            return self._websocket_exception(content)

    async def _general_handler(request: Request, exc: Exception) -> JSONResponse:
        """Default exception handler for all exceptions."""
        body = ExceptionDetail(message=str(exc), code='unknown_error', type=ApiErrorType.SERVER_ERROR, level=ApiErrorLevel.ERROR, status_code=500)
        res = JSONResponse(
            status_code=body.status_code,
            content=body.model_dump(mode="json"),
            headers=None,
        )
        _logger.error(f"General error: {str(exc)}")
        return res


    async def _request_validation_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Exception handler for all request validation errors."""
        body = ExceptionDetail(message=str(exc), code='invalid_data_request', type=ApiErrorType.USER_ERROR, level=ApiErrorLevel.ERROR, status_code=400)
        res = JSONResponse(
            status_code=body.status_code,
            content=body.model_dump(mode="json"),
            headers=None,
        )
        _logger.error(f"Request validation error: {str(exc)}")
        return res


    async def _response_validation_handler(
        request: Request, exc: ResponseValidationError
    ) -> JSONResponse:
        """Exception handler for all response validation errors."""
        body = ExceptionDetail(message=str(exc), code='invalid_data_response', type=ApiErrorType.USER_ERROR, level=ApiErrorLevel.ERROR, status_code=400)
        res = JSONResponse(
            status_code=body.status_code,
            content=body.model_dump(mode="json"),
            headers=None,
        )
        _logger.error(f"Response validation error: {str(exc)}")
        return res


    async def _http_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """Exception handler for HTTPExceptions. It unwraps the HTTPException and returns the detail in a flat JSON response."""
        res = JSONResponse(
            status_code=exc.status_code, content=exc.detail, headers=exc.headers
        )
        _logger.error(f"HTTP error: {str(exc)}")
        return res


    def register_exception_handlers(self, app: FastAPI):
        """Utility to register serveral exception handlers in one go. Catches Exception, HTTPException and Data Validation errors, logs them and responds with a unified json body.

        ```python
        handler.register_exception_handlers(app)
        ```
        """
        app.add_exception_handler(Exception, self._general_handler)
        app.add_exception_handler(FastAPIHTTPException, self._http_handler)
        app.add_exception_handler(RequestValidationError, self._request_validation_handler)
        app.add_exception_handler(ResponseValidationError, self._response_validation_handler)
