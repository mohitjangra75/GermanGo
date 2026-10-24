"""Homepage, the process page and the sundry static pages."""

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_control

from courses.models import Course
from games.models import MapCity
from leads.forms import EnquiryForm
from pricing.models import Plan
from teachers.models import Teacher

from .models import Faq, HeroWord, Highlight, ProcessStep, SiteStat, Testimonial
from .seo import breadcrumb_schema, build_seo, faq_schema


def home(request):
    featured = Course.objects.published().filter(is_featured=True)[:3]
    if not featured:
        featured = Course.objects.published()[:3]

    faqs = list(Faq.objects.filter(is_published=True, page=Faq.Page.HOME))

    context = {
        "hero_words": HeroWord.objects.filter(is_published=True)[:8],
        "featured_courses": featured,
        "plans": Plan.objects.published()[:3],
        "teachers": Teacher.objects.published().filter(is_featured=True)[:4]
        or Teacher.objects.published()[:4],
        "steps": ProcessStep.objects.filter(is_published=True),
        "trust_points": Highlight.objects.filter(
            is_published=True, section=Highlight.Section.TRUST
        ),
        "opportunities": Highlight.objects.filter(
            is_published=True, section=Highlight.Section.OPPORTUNITY
        ),
        "map_cities": [c.as_payload() for c in MapCity.objects.published()],
        "stats": SiteStat.objects.filter(is_published=True)[:4],
        "testimonials": Testimonial.objects.filter(is_published=True)[:3],
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
                faq_schema(faqs and [(f.question, f.answer) for f in faqs] or []),
            ],
        ),
    }
    return render(request, "home/home.html", context)


def process(request):
    faqs = list(Faq.objects.filter(is_published=True, page=Faq.Page.PROCESS))
    context = {
        "steps": ProcessStep.objects.filter(is_published=True),
        "faqs": faqs,
        "teachers": Teacher.objects.published()[:3],
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
