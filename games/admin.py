from django.contrib import admin
from django.db.models import Avg, Count
from django.utils.html import format_html

from .models import GamePlay, MapCity


@admin.register(MapCity)
class MapCityAdmin(admin.ModelAdmin):
    list_display = ("name", "state", "swatch", "map_x", "map_z", "difficulty", "order", "is_published")
    list_editable = ("map_x", "map_z", "difficulty", "order", "is_published")
    list_filter = ("difficulty", "is_published")
    search_fields = ("name", "state", "fun_fact")
    save_on_top = True

    fieldsets = (
        (None, {"fields": ("name", "state", "population", "difficulty")}),
        (
            "Position on the map",
            {
                "fields": (("map_x", "map_z"), "accent_color"),
                "description": "Normalised coordinates: x runs −1 (west) to 1 (east), "
                "z runs −1 (north) to 1 (south). Berlin sits at roughly (0.42, −0.42).",
            },
        ),
        ("Quiz content", {"fields": ("hint", "fun_fact", "german_phrase", "german_phrase_en")}),
        ("Display", {"fields": ("order", "is_published", "slug")}),
    )

    @admin.display(description="Colour")
    def swatch(self, obj):
        return format_html(
            '<span style="display:inline-block;width:18px;height:18px;border-radius:4px;'
            'background:{};border:1px solid #0002"></span>',
            obj.accent_color,
        )


@admin.register(GamePlay)
class GamePlayAdmin(admin.ModelAdmin):
    list_display = ("created_at", "game", "score_display", "seconds", "used_hints")
    list_filter = ("game", "created_at")
    date_hierarchy = "created_at"
    readonly_fields = ("game", "score", "total", "seconds", "used_hints", "created_at", "updated_at")

    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        """Show the headline engagement numbers above the list."""
        stats = GamePlay.objects.aggregate(
            plays=Count("pk"), average=Avg("score"), avg_seconds=Avg("seconds")
        )
        extra_context = extra_context or {}
        extra_context["title"] = (
            f"Game plays — {stats['plays'] or 0} rounds, "
            f"average score {round(stats['average'] or 0, 1)}, "
            f"average {round(stats['avg_seconds'] or 0)}s"
        )
        return super().changelist_view(request, extra_context)

    @admin.display(description="Score", ordering="score")
    def score_display(self, obj):
        colour = "#2A6F52" if obj.percent >= 70 else "#B98600" if obj.percent >= 40 else "#C0261A"
        return format_html(
            '<b style="color:{}">{}/{}</b> ({}%)', colour, obj.score, obj.total, obj.percent
        )
