import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

PRODUCTION = os.environ.get("DJANGO_ENV") == "production"

SECRET_KEY = "x3d1uc-irq&z+1^(mxl--d&%jma*3#lbzl)2ntxmu%5+!gukii"

DEBUG = not PRODUCTION

if PRODUCTION:
    ALLOWED_HOSTS = ["germango.in", "www.germango.in", "localhost", "127.0.0.1"]
    CSRF_TRUSTED_ORIGINS = ["https://germango.in", "https://www.germango.in"]
    SITE_DOMAIN = "germango.in"
    SITE_PROTOCOL = "https"
else:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]", "testserver"]
    SITE_DOMAIN = "localhost:8000"
    SITE_PROTOCOL = "http"

SITE_NAME = "GermanGo"

CONTACT = {
    "email": "jaishree2668mudgal@gmail.com",
    "phone": "+91 95188 51170",
    "whatsapp": "+91 95188 51170",
    "address": "",
    "hours": "Mon–Sat, 9:00–19:00 IST",
}

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    "django.contrib.staticfiles",
    "django_htmx",
    "core",
    "courses",
    "teachers",
    "pricing",
    "games",
    "leads",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_context",
            ],
            "builtins": ["core.templatetags.germango"],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 9},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "/admin/login/"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "GermanGo <jaishree2668mudgal@gmail.com>"

ENQUIRY_NOTIFY_EMAILS = ["jaishree2668mudgal@gmail.com"]

X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

ENQUIRY_RATE_LIMIT = 5

CURTAIN_MODE = "always"

if PRODUCTION:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = False
    SILENCED_SYSTEM_CHECKS = ["security.W008"]
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SECURE_HSTS_SECONDS = 60 * 60
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        },
    }
