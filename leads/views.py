"""The enquiry form: a full page, plus an HTMX-submitted block used sitewide."""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from core.seo import breadcrumb_schema, build_seo
from core.models import Faq
from courses.models import Course
from pricing.models import Plan
from teachers.models import Teacher

from .forms import EnquiryForm
from .services import attach_context, is_rate_limited, notify_team


def _context_objects(request):
    """Resolve the optional course/plan/teacher the form was submitted with."""
    course = plan = teacher = None
    course_slug = request.POST.get("course") or request.GET.get("course")
    plan_id = request.POST.get("plan") or request.GET.get("plan")
    teacher_slug = request.POST.get("teacher") or request.GET.get("teacher")

    if course_slug:
        course = Course.objects.filter(slug=course_slug, is_published=True).first()
    if plan_id and str(plan_id).isdigit():
        plan = Plan.objects.filter(pk=plan_id, is_published=True).first()
    if teacher_slug:
        teacher = Teacher.objects.filter(slug=teacher_slug, is_published=True).first()
    return course, plan, teacher


def submit(request):
    """Handle a submission from any enquiry block on the site.

    Returns a thank-you fragment to HTMX, or redirects back with a message
    when JavaScript is unavailable — so the form works either way.
    """
    if request.method != "POST":
        return redirect("leads:enquiry")

    form = EnquiryForm(request.POST)
    course, plan, teacher = _context_objects(request)
    form_id = request.POST.get("form_id", "enquiry")

    if is_rate_limited(request):
        context = {
            "form": form,
            "form_id": form_id,
            "course": course,
            "plan": plan,
            "teacher": teacher,
            "throttled": True,
        }
        if request.htmx:
            return render(request, "leads/partials/form.html", context, status=429)
        messages.error(request, "You have sent several enquiries already. Please email us instead.")
        return redirect(request.POST.get("source_path") or "leads:enquiry")

    if form.is_valid():
        enquiry = attach_context(
            form.save(commit=False), request, course=course, plan=plan, teacher=teacher
        )
        enquiry.save()
        notify_team(enquiry)

        context = {"enquiry": enquiry, "course": course, "plan": plan, "teacher": teacher}
        if request.htmx:
            return render(request, "leads/partials/thanks.html", context)

        messages.success(
            request, "Thank you — your enquiry is with us. We reply within one working day."
        )
        return redirect("leads:thanks")

    context = {
        "form": form,
        "form_id": form_id,
        "course": course,
        "plan": plan,
        "teacher": teacher,
    }
    if request.htmx:
        return render(request, "leads/partials/form.html", context, status=422)

    return render(request, "leads/enquiry.html", _page_context(request, form=form))


def _page_context(request, form=None):
    course, plan, teacher = _context_objects(request)
    return {
        "form": form or EnquiryForm(),
        "form_id": "enquiry-page",
        "course": course,
        "plan": plan,
        "teacher": teacher,
        "faqs": Faq.objects.filter(is_published=True, page=Faq.Page.ENQUIRY),
        "seo": build_seo(
            title="Talk to us about learning German",
            description="Tell us your level and your goal and we will recommend a "
            "course, a teacher and a start date. We reply within one working day.",
            structured_data=[
                breadcrumb_schema(request, [("Home", "/"), ("Enquire", request.path)])
            ],
        ),
    }


def enquiry(request):
    return render(request, "leads/enquiry.html", _page_context(request))


def thanks(request):
    context = {
        "seo": build_seo(title="Thank you for your enquiry", noindex=True),
    }
    return render(request, "leads/thanks.html", context)
