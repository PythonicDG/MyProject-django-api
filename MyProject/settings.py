"""
Django settings for MyProject project.
"""

from pathlib import Path
import os
import datetime

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-+db#qns$pgyu!huhpnp+uvktmk#9-7^u*%phsfsxncrjfahcm$'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '509d-182-69-81-141.ngrok-free.app',
    '.ngrok-free.app',  # Wildcard for all ngrok domains
]

# CORS & CSRF Configuration
CORS_ALLOW_ALL_ORIGINS = True  # For development only
CORS_ALLOW_CREDENTIALS = True


CSRF_TRUSTED_ORIGINS = [
    'https://509d-182-69-81-141.ngrok-free.app',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    "http://localhost:5500",
]

# Cookie settings for cross-site requests
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True

# Application definition
INSTALLED_APPS = [
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'corsheaders',
    'MyApp',
    'rest_framework',
    'rest_framework.authtoken',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Should be at the top
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'MyProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'MyApp', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ASGI for Hypercorn
ASGI_APPLICATION = 'MyProject.asgi.application'

# Channel layers (basic setup)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'myproject',
        'USER': 'dipak',
        'PASSWORD': 'dipak',
        'HOST': 'localhost',
        'PORT': '5432'
  
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / "static",  
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication & DRF
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

SITE_ID = 1

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 2,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

# Token expiry
TOKEN_TTL = datetime.timedelta(seconds=1000)

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'dipakgaikwadms@gmail.com'
EMAIL_HOST_PASSWORD = 'epfgkbrqivwyxsbc'