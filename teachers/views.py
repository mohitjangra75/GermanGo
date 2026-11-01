"""Teacher directory and profiles."""

from django.http import Http404
from django.shortcuts import redirect, render

from core.content import FAQS
from core.seo import breadcrumb_schema, build_seo, faq_schema
from courses.models import CEFR_LEVELS, Course
from leads.forms import EnquiryForm

from .content import TEACHERS, get_teacher


def teacher_list(request):
    teachers = TEACHERS

    # A one-teacher school has no directory to browse. Send visitors straight
    # to the profile, and let the page become a list again if more are added.
    if not request.htmx and len(teachers) == 1:
        return redirect(teachers[0].get_absolute_url(), permanent=False)

    level = request.GET.get("level", "").strip().upper()
    if level:
        teachers = [teacher for teacher in teachers if level in teacher.levels]

    if request.GET.get("available") == "1":
        teachers = [teacher for teacher in teachers if teacher.is_accepting_students]

    faqs = FAQS["teachers"]
    context = {
        "teachers": teachers,
        "levels": CEFR_LEVELS,
        "filters": {"level": level, "available": request.GET.get("available", "")},
        "total": len(teachers),
    }

    if request.htmx:
        return render(request, "teachers/partials/teacher_grid.html", context)

    context["faqs"] = faqs
    context["seo"] = build_seo(
        title="Meet the teachers",
        description="Qualified, native-speaking German teachers with years of "
        "classroom and exam-preparation experience. See who you would learn with.",
        structured_data=[
            faq_schema([(f.question, f.answer) for f in faqs]),
            breadcrumb_schema(request, [("Home", "/"), ("Teachers", request.path)]),
        ],
    )
    return render(request, "teachers/teacher_list.html", context)


def teacher_detail(request, slug):
    teacher = get_teacher(slug)
    if teacher is None:
        raise Http404("No such teacher.")

    context = {
        "teacher": teacher,
        "teacher_courses": [
            course
            for course in Course.objects.published()
            if teacher.slug in course.teacher_slugs
        ],
        "colleagues": [other for other in TEACHERS if other.slug != teacher.slug][:3],
        "form": EnquiryForm(),
        "form_id": f"teacher-{teacher.slug}",
        "seo": build_seo(
            title=f"{teacher.name} — German teacher",
            description=teacher.headline or teacher.bio[:160],
            og_type="profile",
            structured_data=[
                {
                    "@context": "https://schema.org",
                    "@type": "Person",
                    "name": teacher.name,
                    "jobTitle": teacher.role or "German teacher",
                    "description": teacher.headline or teacher.bio[:200],
                    "knowsLanguage": teacher.languages or ["German"],
                },
                breadcrumb_schema(
                    request,
                    [("Home", "/"), ("Teachers", "/teachers/"), (teacher.name, request.path)],
                ),
            ],
        ),
    }
    return render(request, "teachers/teacher_detail.html", context)
