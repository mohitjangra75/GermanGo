from django.contrib import admin
from django.utils.html import format_html

from .models import Faq, HeroWord, Highlight, ProcessStep, SiteStat, Testimonial

admin.site.site_header = "GermanGo — Site Manager"
admin.site.site_title = "GermanGo admin"
admin.site.index_title = "Courses, teachers, pricing and enquiries"


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "level_reached", "stars", "course", "order", "is_published")
    list_editable = ("order", "is_published")
    list_filter = ("is_published", "rating", "course")
    search_fields = ("name", "quote", "role")
    autocomplete_fields = ("course",)
    fieldsets = (
        (None, {"fields": ("name", "role", "level_reached", "avatar")}),
        ("Quote", {"fields": ("quote", "rating", "course")}),
        ("Display", {"fields": ("order", "is_published")}),
    )

    @admin.display(description="Rating", ordering="rating")
    def stars(self, obj):
        return "★" * obj.rating + "☆" * (5 - obj.rating)


@admin.register(SiteStat)
class SiteStatAdmin(admin.ModelAdmin):
    list_display = ("value", "label", "caption", "order", "is_published")
    list_editable = ("order", "is_published")


@admin.register(ProcessStep)
class ProcessStepAdmin(admin.ModelAdmin):
    list_display = ("number", "title", "icon", "order", "is_published")
    list_editable = ("order", "is_published")
    search_fields = ("title", "body")
    fieldsets = (
        (None, {"fields": ("number", "title", "icon")}),
        (
            "Content",
            {
                "fields": ("body", "detail"),
                "description": "The body shows everywhere; the detail only on the "
                "How it works page.",
            },
        ),
        ("Display", {"fields": ("order", "is_published")}),
    )


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ("question", "page", "order", "is_published")
    list_editable = ("page", "order", "is_published")
    list_filter = ("page", "is_published")
    search_fields = ("question", "answer")


@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "icon", "order", "is_published")
    list_editable = ("section", "order", "is_published")
    list_filter = ("section", "is_published")
    search_fields = ("title", "description")
    fieldsets = (
        (
            None,
            {
                "fields": ("section", "title", "description"),
                "description": "Trust-strip items are a label only. Opportunities "
                "and course perks use the description too.",
            },
        ),
        ("Display", {"fields": ("icon", "accent_color", "order", "is_published")}),
    )


@admin.register(HeroWord)
class HeroWordAdmin(admin.ModelAdmin):
    list_display = ("display_word", "translation", "order", "is_published")
    list_editable = ("order", "is_published")
    search_fields = ("word", "translation")
    fieldsets = (
        (
            None,
            {
                "fields": ("article", "word", "translation"),
                "description": "These float in the homepage 3D scene. Decorative — "
                "eight or so is plenty.",
            },
        ),
        ("Example", {"fields": ("example_de", "example_en")}),
        ("Display", {"fields": ("order", "is_published")}),
    )
