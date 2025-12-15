from .base import *

# Use an in-memory SQLite database for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Set required environment variables for testing
SECRET_KEY = 'a-secret-key-for-testing'
EMAIL_HOST_USER = 'test@example.com'
EMAIL_HOST_PASSWORD = 'testpassword'

# Use a synchronous task runner for Huey in tests
HUEY = {
    'huey_class': 'huey.SqliteHuey',
    'name': 'test_tasks',
    'filename': ':memory:',
    'immediate': True,  # Run tasks synchronously
}
