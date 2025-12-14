from .base import *

DEBUG = False

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Django security checklist settings
# More details here: https://docs.djangoproject.com/en/dev/howto/deployment/checklist/
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HTTP Strict Transport Security settings
# https://docs.djangoproject.com/en/dev/ref/middleware/#http-strict-transport-security
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

USE_HTTPS_IN_ABSOLUTE_URLS = True

# Update your allowed hosts and CSRF trusted origins here.
ALLOWED_HOSTS = [
    "*",
]
CSRF_TRUSTED_ORIGINS = []

# ==============================================================================
# LOGGING CONFIGURATION
# ==============================================================================

LOG_LEVEL = env.str('LOG_LEVEL', default='INFO').upper() # type: ignore
LOG_FILE_PATH = env.str('LOG_FILE_PATH', default=None) # type: ignore

# Use a simple, readable formatter for development, and JSON for production.
formatter = 'simple' if DEBUG else 'json'

# Base handlers: always log to console.
handlers = ['console']

# Add file handler only if the path is specified in the environment.
if LOG_FILE_PATH:
    handlers.append('file')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(module)s %(funcName)s %(lineno)d %(message)s'
        },
        'simple': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{server_time}] {levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': formatter,
            'level': LOG_LEVEL,
        },
    },
    'root': {
        'handlers': handlers,
        'level': LOG_LEVEL,
    },
    'loggers': {
        'django': {
            'handlers': handlers,
            'level': LOG_LEVEL,
            'propagate': False,
        },
        # A specific logger for our application's code.
        'app': {
            'handlers': handlers,
            'level': LOG_LEVEL,
            'propagate': False,
        },
    }
}

# Add file handler config dynamically if path is provided.
if LOG_FILE_PATH:
    LOGGING['handlers']['file'] = {
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': LOG_FILE_PATH,
        'maxBytes': 1024 * 1024 * 5,  # 5 MB
        'backupCount': 5,
        'formatter': 'json',
        'level': LOG_LEVEL,
    }


