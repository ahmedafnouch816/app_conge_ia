"""
Test settings for Django without the chatbot app.
These settings inherit from the main settings but exclude the chatbot application.
Used by server_no_chatbot.py for testing the leave accrual functionality.
"""

from .settings import *

# Remove the chatbot app from INSTALLED_APPS
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'chatbot']

# Force SQLite database for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Disable CSRF for API testing
MIDDLEWARE = [middleware for middleware in MIDDLEWARE if 'csrf' not in middleware.lower()]

# Set DEBUG to true for testing
DEBUG = True

# Simplify logging for testing
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Email backend for testing - prints to console instead of sending
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
