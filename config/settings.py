"""
Django settings for GermanGo — a marketing site for a German language school.

Deliberately simple: SQLite by default, no environment files, no external
services. The few things that must change for production are grouped under
"Production" at the bottom and marked.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

# Replace this before putting the site on a public domain.
SECRET_KEY = "django-insecure-dev-key-replace-me-before-going-live"

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]", "testserver"]

SITE_NAME = "GermanGo"
SITE_DOMAIN = "localhost:8000"
SITE_PROTOCOL = "http"

# Shown in the footer, the contact block and the enquiry confirmation.
CONTACT = {
    "email": "jaishree2668mudgal@gmail.com",
    "phone": "+91 95188 51170",
    "whatsapp": "+91 95188 51170",
    # Classes are live online, so no street address is advertised.
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
    # Third party
    "django_htmx",
    # Local
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

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Authentication — staff only. The public site has no accounts.
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static & media
# ---------------------------------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# Email — enquiries print to the console in development.
# ---------------------------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "GermanGo <jaishree2668mudgal@gmail.com>"

# Where new enquiry notifications are sent.
ENQUIRY_NOTIFY_EMAILS = ["jaishree2668mudgal@gmail.com"]

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------

X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# A single IP may submit this many enquiries per hour before being throttled.
ENQUIRY_RATE_LIMIT = 5

# ---------------------------------------------------------------------------
# Opening curtain
# ---------------------------------------------------------------------------
# "session" — plays once per browser tab. The default: visitors get the brand
#             moment on arrival and never again while they browse.
# "always"  — plays on every page load. Good while designing it; wearing for
#             a real visitor clicking through four pages.
# "off"     — never plays.
#
# Append ?curtain=1 to any URL to force it regardless, which is how to preview
# it without clearing session storage.
CURTAIN_MODE = "always"

# ---------------------------------------------------------------------------
# Production
# ---------------------------------------------------------------------------
# Before deploying, change the four settings below and switch to PostgreSQL
# if you outgrow SQLite. Nothing else needs touching.
#
#   SECRET_KEY = "<a long random string>"
#   DEBUG = False
#   ALLOWED_HOSTS = ["germango.in"]
#   SITE_DOMAIN, SITE_PROTOCOL = "germango.in", "https"
#
# With DEBUG off, the block below hardens cookies and transport automatically.

if not DEBUG:
    CSRF_TRUSTED_ORIGINS = [f"{SITE_PROTOCOL}://{SITE_DOMAIN}"]
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        },
    }
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
