from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base application error carrying an HTTP status code and a message."""

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ConflictError(AppError):
    def __init__(self, message: str = "Resource conflict") -> None:
        super().__init__(message, status.HTTP_409_CONFLICT)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message, status.HTTP_403_FORBIDDEN)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": exc.errors()},
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
