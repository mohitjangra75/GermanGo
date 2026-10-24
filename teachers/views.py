"""Teacher directory and profiles."""

from django.shortcuts import get_object_or_404, redirect, render

from core.models import Faq
from core.seo import breadcrumb_schema, build_seo, faq_schema
from leads.forms import EnquiryForm

from .models import Teacher


def teacher_list(request):
    teachers = Teacher.objects.published().prefetch_related("courses")

    # A one-teacher school has no directory to browse. Send visitors straight
    # to the profile, and let the page become a list again if more are added.
    if not request.htmx and teachers.count() == 1:
        return redirect(teachers.first(), permanent=False)


    level = request.GET.get("level", "").strip().upper()
    if level:
        teachers = teachers.filter(levels_taught__icontains=level)

    if request.GET.get("available") == "1":
        teachers = teachers.filter(is_accepting_students=True)

    faqs = list(Faq.objects.filter(is_published=True, page=Faq.Page.TEACHERS))
    context = {
        "teachers": teachers,
        "levels": ["A1", "A2", "B1", "B2", "C1", "C2"],
        "filters": {"level": level, "available": request.GET.get("available", "")},
        "total": teachers.count(),
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
    teacher = get_object_or_404(
        Teacher.objects.published().prefetch_related("courses"), slug=slug
    )
    context = {
        "teacher": teacher,
        "teacher_courses": teacher.courses.filter(is_published=True),
        "colleagues": Teacher.objects.published().exclude(pk=teacher.pk)[:3],
        "form": EnquiryForm(),
        "form_id": f"teacher-{teacher.pk}",
        "seo": build_seo(
            teacher,
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
                    "knowsLanguage": teacher.language_list or ["German"],
                },
                breadcrumb_schema(
                    request,
                    [("Home", "/"), ("Teachers", "/teachers/"), (teacher.name, request.path)],
                ),
            ],
        ),
    }
    return render(request, "teachers/teacher_detail.html", context)
