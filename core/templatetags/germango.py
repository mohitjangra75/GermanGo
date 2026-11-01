"""Template helpers, registered as builtins (see TEMPLATES['OPTIONS']).

Kept small: each one removes real repetition rather than hiding logic that
belongs in a view.
"""

from __future__ import annotations

import json

from django import template
from django.utils.safestring import mark_safe

from core.seo import SeoData

register = template.Library()

CURRENCY_SYMBOLS = {"INR": "₹", "EUR": "€", "GBP": "£", "USD": "$"}


def group_indian(number: int) -> str:
    """Group digits the Indian way: 120000 → "1,20,000", not "120,000".

    The last three digits are grouped together and everything before them in
    pairs, which is how prices are written and read in India.
    """
    digits = str(abs(int(number)))
    sign = "-" if number < 0 else ""
    if len(digits) <= 3:
        return sign + digits

    last_three, rest = digits[-3:], digits[:-3]
    pairs = []
    while len(rest) > 2:
        pairs.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        pairs.insert(0, rest)
    return sign + ",".join(pairs + [last_three])


@register.filter
def money(amount, currency="INR") -> str:
    """``{{ course.price|money:course.currency }}`` → ``₹18,000`` or ``₹1,20,000``.

    Indian rupees use lakh grouping; everything else uses thousands.
    """
    try:
        value = float(amount)
    except (TypeError, ValueError):
        return ""

    symbol = CURRENCY_SYMBOLS.get(currency, f"{currency} ")
    whole = int(value)

    if value == whole:
        body = group_indian(whole) if currency == "INR" else f"{whole:,}"
    elif currency == "INR":
        body = f"{group_indian(whole)}.{int(round((value - whole) * 100)):02d}"
    else:
        body = f"{value:,.2f}"
    return f"{symbol}{body}"


@register.filter
def split_lines(value: str) -> list[str]:
    return [line.strip() for line in (value or "").splitlines() if line.strip()]


@register.filter
def initials(value) -> str:
    parts = str(value or "").split()
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


@register.filter
def get_item(mapping, key):
    if mapping is None:
        return None
    try:
        return mapping.get(key)
    except AttributeError:
        return None


@register.simple_tag
def json_attr(value) -> str:
    """Serialise a Python value for a ``data-*`` attribute."""
    return mark_safe(json.dumps(value, ensure_ascii=False).replace('"', "&quot;"))


@register.inclusion_tag("components/icon.html")
def icon(name, size=20, css_class=""):
    return {"name": name, "size": size, "css_class": css_class}


@register.inclusion_tag("components/enquiry_block.html", takes_context=True)
def enquiry_block(context, heading="", blurb="", course=None, plan=None, teacher=None, compact=False):
    """The sitewide enquiry CTA.

    Renders its own form instance so a page can carry several blocks without
    them sharing state, and passes the current path so the admin can see
    which page produced the lead.
    """
    from leads.forms import EnquiryForm

    request = context.get("request")
    key = "generic"
    if course is not None:
        key = f"course-{course.slug}"
    elif plan is not None:
        key = f"plan-{plan.slug}"
    elif teacher is not None:
        key = f"teacher-{teacher.slug}"

    return {
        "form": context.get("form") if context.get("form_id") == key else EnquiryForm(),
        "form_id": key,
        "heading": heading or "Talk to us about learning German",
        "blurb": blurb
        or "Tell us your level and your goal. We reply within one working day.",
        "course": course,
        "plan": plan,
        "teacher": teacher,
        "compact": compact,
        "request": request,
        "source_path": request.path if request else "",
        "CONTACT": context.get("CONTACT"),
    }


@register.simple_tag(takes_context=True)
def active_nav(context, *url_names) -> str:
    """Returns ``is-active`` when the current view matches any given name."""
    request = context.get("request")
    match = getattr(request, "resolver_match", None)
    if not match:
        return ""
    current = f"{match.app_name}:{match.url_name}" if match.app_name else match.url_name
    if current in url_names or match.app_name in url_names:
        return "is-active"
    return ""


@register.simple_tag(takes_context=True)
def canonical_url(context) -> str:
    """The page's absolute URL on SITE_DOMAIN, whichever host served it.

    ``SeoData.canonical_url`` needs the request, which a template cannot pass
    to a method, so ``{{ seo.canonical_url }}`` would silently render empty.
    """
    request = context.get("request")
    if request is None:
        return ""
    return (context.get("seo") or SeoData()).canonical_url(request)
