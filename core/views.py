"""Homepage, the process page and the sundry static pages."""

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_control

from courses.models import Course
from games.content import CITIES
from leads.forms import EnquiryForm
from pricing.content import PLANS
from teachers.content import TEACHERS

from .content import (
    FAQS, HERO_WORDS, OPPORTUNITIES, PROCESS_STEPS, STATS, TESTIMONIALS, TRUST_POINTS,
)
from .seo import breadcrumb_schema, build_seo, faq_schema


def home(request):
    courses = Course.objects.published()
    featured = courses.filter(is_featured=True)[:3] or courses[:3]
    teachers = [teacher for teacher in TEACHERS if teacher.is_featured][:4] or TEACHERS[:4]
    faqs = FAQS["home"]

    context = {
        "hero_words": HERO_WORDS[:8],
        "featured_courses": featured,
        "plans": PLANS[:3],
        "teachers": teachers,
        "steps": PROCESS_STEPS,
        "trust_points": TRUST_POINTS,
        "opportunities": OPPORTUNITIES,
        "map_cities": [city.as_payload() for city in CITIES],
        "stats": STATS[:4],
        "testimonials": TESTIMONIALS[:3],
        "faqs": faqs,
        "form": EnquiryForm(),
        "form_id": "home",
        "seo": build_seo(
            title="GermanGo — learn German and speak with confidence",
            description="Live online German courses from A1 to B2 for learners in "
            "India. Small live batches, Goethe and telc preparation. Fees from ₹6,000.",
            structured_data=[
                {
                    "@context": "https://schema.org",
                    "@type": "EducationalOrganization",
                    "name": "GermanGo",
                    "description": "German language school offering courses from A1 to B2.",
                    "url": f"{request.scheme}://{request.get_host()}/",
                },
                faq_schema([(f.question, f.answer) for f in faqs]),
            ],
        ),
    }
    return render(request, "home/home.html", context)


def process(request):
    faqs = FAQS["process"]
    context = {
        "steps": PROCESS_STEPS,
        "faqs": faqs,
        "teachers": TEACHERS[:3],
        "form": EnquiryForm(),
        "form_id": "process",
        "seo": build_seo(
            title="How learning with us works",
            description="From your first enquiry to your first conversation: the "
            "placement chat, the course match, the teacher and the schedule.",
            structured_data=[
                faq_schema([(f.question, f.answer) for f in faqs]),
                breadcrumb_schema(request, [("Home", "/"), ("How it works", request.path)]),
            ],
        ),
    }
    return render(request, "home/process.html", context)


@cache_control(max_age=60 * 60 * 24)
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Allow: /",
        "",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
