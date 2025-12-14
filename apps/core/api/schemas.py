from ninja import Schema
from typing import List

class ErrorDetail(Schema):
    field: str
    message: str

class ValidationErrorResponse(Schema):
    detail: str
    errors: List[ErrorDetail]

class AuthenticationErrorResponse(Schema):
    detail: str

class AuthorizationErrorResponse(Schema):
    detail: str

class NotFoundErrorResponse(Schema):
    detail: str

class HttpErrorResponse(Schema):
    detail: str

class BaseAPIExceptionResponse(Schema):
    detail: str

class GenericErrorResponse(Schema):
    detail: str
    error_type: str | None = None
    error_message: str | None = None
