"""
Django settings for the_spymaster project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import logging
import os
import sys
from pathlib import Path

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from the_spymaster.utils import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = config.django_debug
SECRET_KEY = config.django_secret_key
SITE_ID = 1
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

if DEBUG:
    sentry_sdk.init(
        dsn=config.sentry_dsn,
        integrations=[DjangoIntegration(), LoggingIntegration(event_level=None)],
        environment=config.env_verbose_name,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
    )

# Application definition

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Rest
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    # Auth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    # App
    "api",
]

MIDDLEWARE = [
    # "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "api.middleware.SpymasterExceptionHandlerMiddleware",
]
if DEBUG:
    MIDDLEWARE += ["qinspect.middleware.QueryInspectMiddleware"]

ROOT_URLCONF = "the_spymaster.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "the_spymaster.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Jerusalem"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Logging
LOGS_PARENT = BASE_DIR  # if DEBUG else os.path.join(BASE_DIR, "../")
LOGGING_DIR = os.path.join(LOGS_PARENT, "logs")
os.makedirs(LOGGING_DIR, exist_ok=True)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[%(asctime)s.%(msecs)03d] [%(levelname)-.4s]: %(message)s [%(name)s]",
            "datefmt": "%H:%M:%S",
        },
        "debug": {
            "class": "the_spymaster.utils.logging.ContextFormatter",
            "format": "[%(asctime)s.%(msecs)03d] [%(levelname)-.4s]: %(message)s @@@ "
            "[%(name)s:%(lineno)s] [%(threadName)s]",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "()": "the_spymaster.utils.logging.JsonFormatter",
            "indented": config.indented_json,
        },
    },
    "filters": {
        "std_filter": {"()": "the_spymaster.utils.logging.LevelRangeFilter", "high": logging.WARNING},
        "err_filter": {"()": "the_spymaster.utils.logging.LevelRangeFilter", "low": logging.WARNING},
    },
    "handlers": {
        "console_out": {
            "class": "logging.StreamHandler",
            "filters": ["std_filter"],
            "formatter": config.formatter,
            "stream": sys.stdout,
        },
        "console_err": {
            "class": "logging.StreamHandler",
            "filters": ["err_filter"],
            "formatter": config.formatter,
            "stream": sys.stderr,
        },
        "spymaster_file": {
            "class": "logging.handlers.WatchedFileHandler",
            "filename": os.path.join(LOGGING_DIR, "spymaster.log"),
            "formatter": "debug",
            "level": "DEBUG",
        },
        "root_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOGGING_DIR, "root.log"),
            "formatter": "json",
            "level": "INFO",
            "when": "midnight",
            "backupCount": 14,
        },
        "django_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOGGING_DIR, "debug.log"),
            "formatter": "json",
            "when": "midnight",
            "backupCount": 7,
        },
    },
    "root": {"handlers": ["console_out", "console_err", "root_file"], "level": config.root_log_level},
    "loggers": {
        "api": {
            "handlers": ["spymaster_file", "console_out", "console_err"],
            "level": "DEBUG",
            "propagate": False,
        },
        # 3rd parties
        "telegram": {"level": "INFO"},
        "apscheduler": {"level": "INFO"},
        "qinspect": {"level": "DEBUG"},
        # Django
        "django": {"handlers": ["django_file", "console_err"], "level": "DEBUG", "propagate": False},
        "django.utils.autoreload": {"level": "INFO"},
    },
}

# Auth
AUTH_USER_MODEL = "api.SpymasterUser"
LOGIN_REDIRECT_URL = "login_complete"
LOGOUT_REDIRECT_URL = "index"
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http" if DEBUG else "https"
GOOGLE_OAUTH_CLIENT_ID = config.google_oauth_client_id
GOOGLE_OAUTH_CLIENT_SECRET = config.google_oauth_client_secret

# CAPTCHA
RECAPTCHA_SITE_KEY = config.recaptcha_site_key
RECAPTCHA_PRIVATE_KEY = config.recaptcha_private_key
SILENCED_SYSTEM_CHECKS = ["captcha.recaptcha_test_key_error"]

# Social Account
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ]
    }
}
SOCIALACCOUNT_ADAPTER = "api.views.social_hooks.CustomSocialAccountAdapter"

# REST
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "10/hour",
    },
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "PAGE_SIZE": 50,
}

# Query inspect
QUERY_INSPECT_ENABLED = DEBUG
QUERY_INSPECT_LOG_QUERIES = DEBUG
