"""The pricing page."""

from django.shortcuts import render

from core.content import FAQS, TESTIMONIALS
from core.seo import breadcrumb_schema, build_seo, faq_schema
from courses.models import Course
from leads.forms import EnquiryForm

from .content import PLANS


def pricing(request):
    faqs = FAQS["pricing"]

    context = {
        "plans": PLANS,
        "courses": Course.objects.published()[:6],
        "faqs": faqs,
        "testimonials": TESTIMONIALS[:2],
        "form": EnquiryForm(),
        "form_id": "pricing",
        "seo": build_seo(
            title="German course fees in India",
            description="Transparent fees in rupees for batch, one-to-one and "
            "intensive German courses. No admission fee and no hidden extras.",
            structured_data=[
                faq_schema([(f.question, f.answer) for f in faqs]),
                breadcrumb_schema(request, [("Home", "/"), ("Pricing", request.path)]),
            ],
        ),
    }
    return render(request, "pricing/pricing.html", context)
