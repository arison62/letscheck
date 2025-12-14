from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# If use HMR or not.
DJANGO_VITE = {
    "default": {
        "dev_mode": DEBUG,
        "dev_server_host": env.str("DJANGO_VITE_DEV_SERVER_HOST", default="localhost"), # type: ignore
        "dev_server_port": env.int("DJANGO_VITE_DEV_SERVER_PORT", default=5173), # type: ignore
    }
}

# Debug toolbar settings
INTERNAL_IPS = [
    "127.0.0.1",
]

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


