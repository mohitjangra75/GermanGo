"""Values every template needs: site identity and contact details."""

from django.conf import settings


def site_context(request):
    return {
        "SITE_NAME": settings.SITE_NAME,
        "SITE_DOMAIN": settings.SITE_DOMAIN,
        "SITE_PROTOCOL": settings.SITE_PROTOCOL,
        "CONTACT": settings.CONTACT,
        "CURTAIN_MODE": getattr(settings, "CURTAIN_MODE", "session"),
        "is_htmx": bool(getattr(request, "htmx", False)),
    }
