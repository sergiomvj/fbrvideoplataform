from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, message: str, status_code: int) -> None:
        self.message = message
        self.status_code = status_code


def create_unauthorized_response() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail="Authentication required",
    )


def create_forbidden_response() -> HTTPException:
    return HTTPException(
        status_code=403,
        detail="Access denied",
    )


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message},
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )
