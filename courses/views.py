"""Course catalogue and course detail — both aimed at an enquiry."""

from django.shortcuts import get_object_or_404, render

from core.content import FAQS, OPPORTUNITIES, TESTIMONIALS
from core.seo import breadcrumb_schema, build_seo, course_schema, faq_schema
from leads.forms import EnquiryForm
from pricing.content import plans_covering

from .models import CEFR_LEVELS, Course


def course_list(request):
    courses = Course.objects.published()

    level = request.GET.get("level", "").strip().upper()
    if level in CEFR_LEVELS:
        courses = courses.filter(level_code=level)

    course_format = request.GET.get("format", "").strip()
    if course_format:
        courses = courses.filter(course_format=course_format)

    delivery = request.GET.get("delivery", "").strip()
    if delivery:
        courses = courses.filter(delivery=delivery)

    context = {
        "courses": courses,
        "levels": CEFR_LEVELS,
        "formats": Course.Format.choices,
        "deliveries": Course.Delivery.choices,
        "filters": {"level": level, "format": course_format, "delivery": delivery},
        "total": courses.count(),
    }

    # HTMX filter requests only need the results grid.
    if request.htmx:
        return render(request, "courses/partials/course_grid.html", context)

    faqs = FAQS["courses"]
    context["faqs"] = faqs
    context["testimonials"] = TESTIMONIALS[:3]
    context["opportunities"] = OPPORTUNITIES
    context["seo"] = build_seo(
        title="German course fees and batches — A1 to B2",
        description="Small-batch, one-to-one and intensive German courses at every "
        "CEFR level. See dates, fees in rupees and batch sizes, then talk to us.",
        structured_data=[
            faq_schema([(f.question, f.answer) for f in faqs]),
            breadcrumb_schema(request, [("Home", "/"), ("Courses", request.path)]),
        ],
    )
    return render(request, "courses/course_list.html", context)


def course_detail(request, slug):
    course = get_object_or_404(Course.objects.published(), slug=slug)
    others = Course.objects.published().exclude(pk=course.pk)
    related = others.filter(level_code=course.level_code)[:3] or others[:3]

    context = {
        "course": course,
        "modules": course.modules.all(),
        "course_teachers": course.teachers,
        "plans": plans_covering(course),
        "related": related,
        "testimonials": [t for t in TESTIMONIALS if t.course == course.slug][:2],
        "form": EnquiryForm(),
        "form_id": f"course-{course.slug}",
        "seo": build_seo(
            title=f"{course.title} — German {course.level_code}",
            description=course.subtitle or course.description[:160],
            structured_data=[
                course_schema(course),
                breadcrumb_schema(
                    request,
                    [("Home", "/"), ("Courses", "/courses/"), (course.title, request.path)],
                ),
            ],
        ),
    }
    return render(request, "courses/course_detail.html", context)
