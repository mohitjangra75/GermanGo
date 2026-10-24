from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html

from .models import Course, CourseModule


class CourseModuleInline(admin.StackedInline):
    model = CourseModule
    extra = 1
    fields = (("order", "week_range"), "title", "summary", "topics")
    ordering = ("order",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "level_code",
        "course_format",
        "delivery",
        "price_display",
        "duration_display",
        "next_start_date",
        "enquiry_count",
        "is_featured",
        "is_published",
    )
    list_editable = ("is_featured", "is_published")
    list_filter = ("level_code", "course_format", "delivery", "is_published", "is_featured")
    search_fields = ("title", "subtitle", "description")
    filter_horizontal = ("teachers",)
    inlines = [CourseModuleInline]
    save_on_top = True
    date_hierarchy = "next_start_date"

    fieldsets = (
        (None, {"fields": ("title", "level_code", "subtitle", "description")}),
        (
            "Selling points",
            {
                "fields": ("who_is_it_for", "outcomes"),
                "description": "One item per line. Both render as tick lists.",
            },
        ),
        (
            "Format & schedule",
            {
                "fields": (
                    ("course_format", "delivery"),
                    ("duration_weeks", "hours_per_week", "max_class_size"),
                    "schedule_note",
                    "next_start_date",
                )
            },
        ),
        ("Price", {"fields": (("price", "currency"),)}),
        ("Teachers", {"fields": ("teachers",)}),
        (
            "Presentation",
            {"fields": ("cover_image", "accent_color", "badge", "order", "is_featured", "is_published")},
        ),
        (
            "SEO",
            {
                "classes": ("collapse",),
                "fields": ("slug", "seo_title", "seo_description", "og_image", "noindex"),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_enquiries=Count("enquiries"))

    @admin.display(description="Price", ordering="price")
    def price_display(self, obj):
        from core.templatetags.germango import money

        return money(obj.price, obj.currency)

    @admin.display(description="Duration")
    def duration_display(self, obj):
        return f"{obj.duration_weeks} wks · {obj.total_hours:g} h"

    @admin.display(description="Enquiries", ordering="_enquiries")
    def enquiry_count(self, obj):
        if not obj._enquiries:
            return "—"
        url = reverse("admin:leads_enquiry_changelist")
        return format_html('<a href="{}?course__id__exact={}">{}</a>', url, obj.pk, obj._enquiries)


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "week_range", "order")
    list_filter = ("course",)
    search_fields = ("title", "summary", "topics")
    autocomplete_fields = ("course",)
