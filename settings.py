# Define DEBUG variable
from decouple import config  # Ensure this is imported for environment variable management
import dj_database_url  # Ensure this is imported for database configuration

DEBUG = config('DEBUG', default='False') == 'True'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Replace with your email provider's SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'habrovan14@gmail.com'  # Replace with your email
EMAIL_HOST_PASSWORD = 'nmim szaf comz eshh'  # Replace with your email password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER  # Ensure it matches the host user for consistency

# Ensure emails are sent as HTML by default
DEFAULT_EMAIL_CONTENT_TYPE = 'html'

# Add an email backend for debugging
if DEBUG:  # Ensure this is only for development
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

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
        'level': 'DEBUG',
    },
}

EMAIL_VERIFICATION_URL = 'http://127.0.0.1:8000/verify-email/'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Default backend
]

# Optional: If using a custom user model
# AUTH_USER_MODEL = 'your_app_name.CustomUser'

# Security settings
SECURE_HSTS_SECONDS = 31536000  # Enable HSTS for 1 year
SECURE_SSL_REDIRECT = True      # Redirect all HTTP traffic to HTTPS
SESSION_COOKIE_SECURE = True    # Use secure cookies for sessions
CSRF_COOKIE_SECURE = True       # Use secure cookies for CSRF tokens

# Ensure SECRET_KEY is strong and secure
import os
from django.core.management.utils import get_random_secret_key

SECRET_KEY = config('SECRET_KEY', default='your-very-strong-and-random-secret-key')

# Ensure BASE_DIR is defined for STATIC_ROOT
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configure for Render
ALLOWED_HOSTS = ['*']  # Or your specific domain
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# DATABASES configuration using dj_database_url
DATABASES = {
    'default': dj_database_url.config(default=config('DATABASE_URL'))
}

# Feature X configuration
FEATURE_X_ENABLED = True
FEATURE_X_PARAMETER_1 = "value1"
FEATURE_X_PARAMETER_2 = "value2"