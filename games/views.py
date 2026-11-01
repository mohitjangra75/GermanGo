"""The Germany map quiz page and its result endpoint.

Nothing about a round is saved: the score is checked, turned into a result
card with a course CTA, and forgotten.
"""

from dataclasses import dataclass

from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from core.content import FAQS
from core.seo import breadcrumb_schema, build_seo
from courses.models import Course
from leads.forms import EnquiryForm

from .content import CITIES

# A round is this many cities, drawn from the full list.
ROUND_LENGTH = 8


@dataclass(frozen=True)
class Round:
    """One finished round, as shown on the result card."""

    score: int
    total: int
    seconds: int = 0
    used_hints: int = 0

    @property
    def percent(self) -> int:
        return round(self.score * 100 / self.total) if self.total else 0

    @property
    def verdict(self) -> str:
        """The headline shown on the result card."""
        percent = self.percent
        if percent == 100:
            return "Perfekt!"
        if percent >= 80:
            return "Sehr gut!"
        if percent >= 60:
            return "Nicht schlecht!"
        if percent >= 40:
            return "Ganz okay."
        return "Übung macht den Meister."


def map_quiz(request):
    context = {
        "cities": CITIES,
        "city_data": [city.as_payload() for city in CITIES],
        "round_length": min(ROUND_LENGTH, len(CITIES)),
        "courses": Course.objects.published()[:3],
        "form": EnquiryForm(),
        "form_id": "map-quiz",
        "faqs": FAQS["home"][:3],
        "seo": build_seo(
            title="German map quiz — how well do you know Germany?",
            description="Find Berlin, Munich, Hamburg and more on an interactive 3D "
            "map of Germany. A two-minute game, and a useful one if you are "
            "planning to move there.",
            structured_data=[
                breadcrumb_schema(request, [("Home", "/"), ("Map quiz", request.path)])
            ],
        ),
    }
    return render(request, "games/map_quiz.html", context)


@require_POST
def map_quiz_result(request):
    """Return the result card for a finished round, with a CTA."""
    try:
        total = max(0, min(50, int(request.POST.get("total", 0))))
        score = max(0, min(total, int(request.POST.get("score", 0))))
        seconds = max(0, min(3600, int(request.POST.get("seconds", 0))))
        hints = max(0, min(50, int(request.POST.get("hints", 0))))
    except (TypeError, ValueError):
        return HttpResponseBadRequest("Scores must be whole numbers.")

    if not total:
        return HttpResponseBadRequest("A round needs at least one question.")

    if not request.htmx:
        return redirect("games:map_quiz")

    context = {
        "play": Round(score=score, total=total, seconds=seconds, used_hints=hints),
        "courses": Course.objects.published()[:3],
        "form": EnquiryForm(),
        "form_id": "map-quiz",
    }
    return render(request, "games/partials/result.html", context)
