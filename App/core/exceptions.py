from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder


class AppError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        code: str = "BUSINESS_ERROR",
        details=None,
    ):
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or []


def err(
    request: Request,
    status: int,
    message: str,
    code: str,
    details=None,
):
    content = {
        "success": False,
        "message": message,
        "error": {
            "code": code,
            "details": details or [],
        },
        "request_id": getattr(request.state, "request_id", None),
    }

    return JSONResponse(
        status_code=status,
        content=jsonable_encoder(content),
    )


async def app_error_handler(request: Request, exc: AppError):
    return err(
        request,
        exc.status_code,
        exc.message,
        exc.code,
        exc.details,
    )


async def validation_handler(
    request: Request,
    exc: RequestValidationError,
):
    details = []

    for error in exc.errors():
        clean_error = {
            "type": error.get("type"),
            "location": error.get("loc"),
            "message": error.get("msg"),
            "input": error.get("input"),
        }

        if error.get("ctx"):
            clean_error["context"] = {
                key: str(value)
                for key, value in error["ctx"].items()
            }

        details.append(clean_error)

    return err(
        request,
        422,
        "Request validation failed",
        "VALIDATION_ERROR",
        details,
    )


async def unexpected_handler(
    request: Request,
    exc: Exception,
):
    return err(
        request,
        500,
        "An unexpected server error occurred",
        "INTERNAL_ERROR",
    )