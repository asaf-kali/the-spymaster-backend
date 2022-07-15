"""
Django settings for the_spymaster project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
from pathlib import Path

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from the_spymaster_util import get_dict_config

from the_spymaster.config import get_config

config = get_config()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
ENVIRONMENT = config.env_verbose_name
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEBUG = config.django_debug
SECRET_KEY = config.django_secret_key
SITE_ID = 1
ALLOWED_HOSTS = ["backend.the-spymaster.xyz", "backend.dev.the-spymaster.xyz", "localhost", "127.0.0.1"]

sentry_sdk.init(  # type: ignore
    dsn=config.sentry_dsn,
    integrations=[LoggingIntegration(event_level=None)],
    environment=ENVIRONMENT,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=0.2,
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
    # Utils
    "django_json_widget",
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
    "api.middleware.ContextLoggingMiddleware",
    "api.middleware.SpymasterExceptionHandlerMiddleware",
]
if config.env_name == "local":
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
        "ENGINE": config.get("DB_ENGINE") or "django.db.backends.sqlite3",
        "NAME": config.get("DB_NAME") or BASE_DIR / "db.sqlite3",
        "USER": config.get("DB_USER"),
        "PASSWORD": config.get("DB_PASSWORD"),
        "HOST": config.get("DB_HOST"),
        "PORT": config.get("DB_PORT"),
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
loggers = {
    "api": {
        "handlers": ["console_out", "console_err"],
        "level": "DEBUG",
        "propagate": False,
    },
    "codenames": {
        "handlers": ["console_out", "console_err"],
        "level": "DEBUG",
        "propagate": False,
    },
    "codenames.utils": {
        "level": "INFO",
    },
    # 3rd parties
    "apscheduler": {"level": "INFO"},
    "qinspect": {"level": "DEBUG"},
    "mangum.http": {"level": "WARNING"},
    "urllib3": {"level": "WARNING"},
    "urllib3.util.retry": {"level": "DEBUG"},
    # Django
    "django": {"handlers": ["console_err"], "level": "DEBUG", "propagate": False},
    "django.utils.autoreload": {"level": "INFO"},
}
LOGGING = get_dict_config(
    std_formatter=config.std_formatter,
    root_log_level=config.root_log_level,
    indent_json=config.indent_json,
    extra_loggers=loggers,
)

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
