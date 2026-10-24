"""Page metadata helpers.

Views build an ``SeoData`` and put it in the context as ``seo``; base.html
renders the title, description, canonical URL, Open Graph tags and JSON-LD
from it, so no template hand-writes a meta tag.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from django.conf import settings
from django.utils.safestring import mark_safe

DEFAULT_DESCRIPTION = (
    "Live online German courses from A1 to B2 for learners in India. Small "
    "batches, Goethe and telc exam preparation, fees from ₹6,000."
)


@dataclass
class SeoData:
    title: str = ""
    description: str = ""
    canonical_path: str = ""
    og_image: str = ""
    og_type: str = "website"
    noindex: bool = False
    structured_data: list[dict] = field(default_factory=list)

    @property
    def full_title(self) -> str:
        if not self.title:
            return f"{settings.SITE_NAME} — German language school"
        if settings.SITE_NAME.lower() in self.title.lower():
            return self.title
        return f"{self.title} | {settings.SITE_NAME}"

    @property
    def meta_description(self) -> str:
        return self.description or DEFAULT_DESCRIPTION

    def canonical_url(self, request) -> str:
        path = self.canonical_path or request.path
        return f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}{path}"

    def json_ld(self) -> str:
        blocks = [b for b in self.structured_data if b]
        if not blocks:
            return ""
        payload = blocks[0] if len(blocks) == 1 else blocks
        return mark_safe(json.dumps(payload, ensure_ascii=False))


def build_seo(obj=None, **overrides) -> SeoData:
    """Build page metadata, preferring per-object admin overrides."""
    data = SeoData(**overrides)
    if obj is not None:
        data.title = getattr(obj, "seo_title", "") or data.title
        data.description = getattr(obj, "seo_description", "") or data.description
        data.noindex = bool(getattr(obj, "noindex", False)) or data.noindex
        image = getattr(obj, "og_image", None)
        if image:
            try:
                data.og_image = image.url
            except ValueError:
                pass
    return data


def course_schema(course) -> dict:
    schema = {
        "@context": "https://schema.org",
        "@type": "Course",
        "name": course.title,
        "description": course.seo_description or course.subtitle or course.description[:200],
        "provider": {
            "@type": "EducationalOrganization",
            "name": settings.SITE_NAME,
            "sameAs": f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}/",
        },
        "educationalLevel": course.level_code,
        "inLanguage": "de",
        "teaches": "German language",
        "hasCourseInstance": {
            "@type": "CourseInstance",
            "courseMode": "online" if course.delivery == "online" else "blended",
            "courseWorkload": f"PT{course.total_hours:g}H",
        },
    }
    if course.price:
        schema["offers"] = {
            "@type": "Offer",
            "price": str(course.price),
            "priceCurrency": course.currency,
            "category": "Paid",
        }
    return schema


def faq_schema(pairs) -> dict | None:
    pairs = list(pairs or [])
    if not pairs:
        return None
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {"@type": "Answer", "text": answer},
            }
            for question, answer in pairs
        ],
    }


def breadcrumb_schema(request, crumbs) -> dict:
    base = f"{settings.SITE_PROTOCOL}://{settings.SITE_DOMAIN}"
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": name, "item": f"{base}{path}"}
            for i, (name, path) in enumerate(crumbs, start=1)
        ],
    }
