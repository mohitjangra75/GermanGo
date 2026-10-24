"""Settings for serving the site publicly through a Cloudflare tunnel.

Kept separate from `settings.py` so day-to-day development is untouched:
that file stays on DEBUG with SQLite and no ceremony. Run this one with

    DJANGO_SETTINGS_MODULE=config.settings_live gunicorn config.wsgi

Everything security-related is declared explicitly here rather than relying
on the `if not DEBUG` block in the base settings, because that block has
already been evaluated by the time this module overrides DEBUG.
"""

from .settings import *  # noqa: F401,F403

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

DEBUG = False

SECRET_KEY = "x3d1uc-irq&z+1^(mxl--d&%jma*3#lbzl)2ntxmu%5+!gukii"

# Quick tunnels get a fresh random subdomain each run, so the whole domain is
# trusted rather than one host. Add your own domain here when you have one.
ALLOWED_HOSTS = [
    ".trycloudflare.com",
    ".cfargotunnel.com",
    "localhost",
    "127.0.0.1",
]

CSRF_TRUSTED_ORIGINS = [
    "https://*.trycloudflare.com",
    "https://*.cfargotunnel.com",
]

SITE_DOMAIN = "revolution-programmers-classified-assessed.trycloudflare.com"
SITE_PROTOCOL = "https"

# ---------------------------------------------------------------------------
# Transport
# ---------------------------------------------------------------------------

# Cloudflare terminates TLS and forwards plain HTTP to gunicorn, so Django
# must read the protocol from the forwarded header. Redirecting to HTTPS
# ourselves would loop, because the request arriving here is always HTTP.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = False

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# No HSTS on a temporary preview host: it would pin a domain that stops
# existing when the tunnel closes.
SECURE_HSTS_SECONDS = 0

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

# Still the console backend: no SMTP credentials are configured, and silently
# dropping enquiries would be worse than printing them to the server log.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
