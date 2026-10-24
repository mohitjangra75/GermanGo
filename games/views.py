"""The Germany map quiz page and its result endpoint."""

from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from core.models import Faq
from core.seo import breadcrumb_schema, build_seo
from courses.models import Course
from leads.forms import EnquiryForm

from .models import GamePlay, MapCity

# A round is this many cities, drawn from whatever is published.
ROUND_LENGTH = 8


def map_quiz(request):
    cities = list(MapCity.objects.published())
    context = {
        "cities": cities,
        "city_data": [city.as_payload() for city in cities],
        "round_length": min(ROUND_LENGTH, len(cities)),
        "courses": Course.objects.published()[:3],
        "form": EnquiryForm(),
        "form_id": "map-quiz",
        "faqs": Faq.objects.filter(is_published=True, page=Faq.Page.HOME)[:3],
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
    """Record a finished round and return the result card with a CTA."""
    try:
        total = max(0, min(50, int(request.POST.get("total", 0))))
        score = max(0, min(total, int(request.POST.get("score", 0))))
        seconds = max(0, min(3600, int(request.POST.get("seconds", 0))))
        hints = max(0, min(50, int(request.POST.get("hints", 0))))
    except (TypeError, ValueError):
        return HttpResponseBadRequest("Scores must be whole numbers.")

    if not total:
        return HttpResponseBadRequest("A round needs at least one question.")

    play = GamePlay.objects.create(
        game=GamePlay.Game.MAP_QUIZ,
        score=score,
        total=total,
        seconds=seconds,
        used_hints=hints,
    )

    context = {
        "play": play,
        "courses": Course.objects.published()[:3],
        "form": EnquiryForm(),
        "form_id": "map-quiz",
    }
    if not request.htmx:
        return redirect("games:map_quiz")
    return render(request, "games/partials/result.html", context)
