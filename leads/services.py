"""Saving an enquiry, throttling abuse and notifying the school."""

from __future__ import annotations

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.template.loader import render_to_string


def client_ip(request) -> str:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def is_rate_limited(request) -> bool:
    """True once an IP has sent more than the allowed enquiries this hour."""
    limit = getattr(settings, "ENQUIRY_RATE_LIMIT", 5)
    ip = client_ip(request)
    if not ip:
        return False
    key = f"enquiry-rate:{ip}"
    count = cache.get(key, 0)
    if count >= limit:
        return True
    # Cache.add sets the TTL only on the first write, so the window is a
    # fixed hour from the first enquiry rather than a rolling reset.
    cache.add(key, 0, timeout=3600)
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=3600)
    return False


def attach_context(enquiry, request, course=None, plan=None, teacher=None):
    """Record where the enquiry came from, so the school can follow up well."""
    enquiry.course = course.title if course else ""
    enquiry.plan = plan.name if plan else ""
    enquiry.teacher = teacher.name if teacher else ""
    enquiry.source_path = (request.POST.get("source_path") or request.path)[:300]
    enquiry.referrer = request.META.get("HTTP_REFERER", "")[:300]
    return enquiry


def notify_team(enquiry) -> None:
    """Email the school. Failures never block the visitor's confirmation."""
    recipients = getattr(settings, "ENQUIRY_NOTIFY_EMAILS", [])
    if not recipients:
        return
    subject = f"New enquiry — {enquiry.name} ({enquiry.interest})"
    body = render_to_string("leads/email/new_enquiry.txt", {"enquiry": enquiry})
    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            recipients,
            fail_silently=True,
        )
    except Exception:  # noqa: BLE001 -- notification must never break the form
        pass
