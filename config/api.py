
from django.http import Http404, HttpRequest
from django.conf import settings
from ninja import NinjaAPI
from ninja.throttling import AnonRateThrottle, AuthRateThrottle
from apps.verifications.api import router as verifications_router
from ninja.errors import ValidationError, HttpError, AuthenticationError, AuthorizationError

import logging
from apps.core.api.exceptions import BaseAPIException
from apps.core.api.schemas import (
    ValidationErrorResponse,
    AuthenticationErrorResponse,
    AuthorizationErrorResponse,
    NotFoundErrorResponse,
    HttpErrorResponse,
    BaseAPIExceptionResponse,
    ErrorDetail,
    GenericErrorResponse
)


logger = logging.getLogger("app")


# Instanciation de l'API
api_v1 = NinjaAPI(
    title="Let's Check API V1",
    version="1.0.0",
    description="API V1 for Let's Check platform.",
    throttle=[
        AnonRateThrottle('10/s'),
        AuthRateThrottle('100/s')
    ]
)

api_v1.add_router("/verifications", verifications_router, tags=["Verifications"])

# Gestionnaires d'exceptions globaux avec schémas pour docs Swagger
@api_v1.exception_handler(ValidationError)
def validation_errors(request: HttpRequest, exc: ValidationError):
    errors = []
    for error in exc.errors:
        field = ".".join(map(str, error['loc'])) if error['loc'] else 'non_field_error'
        errors.append(ErrorDetail(field=field, message=error['msg']))
    response_data = ValidationErrorResponse(detail="Erreur de validation.", errors=errors)
    return api_v1.create_response(request, response_data, status=422)

@api_v1.exception_handler(AuthenticationError)
def authentication_error(request: HttpRequest, exc: AuthenticationError):
    response_data = AuthenticationErrorResponse(detail="Authentification requise. Veuillez fournir des identifiants valides.")
    return api_v1.create_response(request, response_data, status=401)

@api_v1.exception_handler(AuthorizationError)
def authorization_error(request: HttpRequest, exc: AuthorizationError):
    response_data = AuthorizationErrorResponse(detail="Permission refusée. Vous n'avez pas les droits nécessaires pour effectuer cette action.")
    return api_v1.create_response(request, response_data, status=403)

@api_v1.exception_handler(Http404)
def not_found(request: HttpRequest, exc: Http404):
    response_data = NotFoundErrorResponse(detail="La ressource demandée n'a pas été trouvée.")
    return api_v1.create_response(request, response_data, status=404)

@api_v1.exception_handler(HttpError)
def http_error(request: HttpRequest, exc: HttpError):
    response_data = HttpErrorResponse(detail=exc.message)
    return api_v1.create_response(request, response_data, status=exc.status_code)

@api_v1.exception_handler(BaseAPIException)
def custom_api_error(request: HttpRequest, exc: BaseAPIException):
    response_data = BaseAPIExceptionResponse(detail=exc.detail)
    return api_v1.create_response(request, response_data, status=exc.status_code)

@api_v1.exception_handler(Exception)
def generic_exception_handler(request: HttpRequest, exc: Exception):
    logger.error(f"Erreur non gérée sur {request.path}: {exc}", exc_info=True)
    if settings.DEBUG:
        response_data = GenericErrorResponse(
            detail="Une erreur interne est survenue.",
            error_type=type(exc).__name__,
            error_message=str(exc)
        )
    else:
        response_data = GenericErrorResponse(detail="Une erreur inattendue est survenue. L'équipe technique a été notifiée.")
    return api_v1.create_response(request, response_data, status=500)