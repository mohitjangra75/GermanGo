from django import forms
from django.contrib import admin

from core.templatetags.germango import money
from teachers.content import TEACHERS

from .models import Course, CourseModule


class CourseModuleInline(admin.StackedInline):
    model = CourseModule
    extra = 0
    fields = (("order", "week_range"), "title", "summary", "topics")


class CourseForm(forms.ModelForm):
    # Teachers live in teachers/content.py, so pick them from that list.
    teacher_slugs = forms.MultipleChoiceField(
        label="Teachers",
        choices=lambda: [(teacher.slug, teacher.name) for teacher in TEACHERS],
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Course
        fields = "__all__"


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    form = CourseForm
    list_display = (
        "title",
        "level_code",
        "course_format",
        "price_display",
        "duration_display",
        "next_start_date",
        "order",
        "is_featured",
        "is_published",
    )
    list_editable = ("order", "is_featured", "is_published")
    list_filter = ("level_code", "course_format", "is_published", "is_featured")
    search_fields = ("title", "subtitle", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [CourseModuleInline]
    save_on_top = True

    fieldsets = (
        (None, {"fields": ("title", "slug", "level_code", "subtitle", "description")}),
        (
            "Selling points",
            {
                "fields": ("audience", "outcomes"),
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
        ("Price", {"fields": ("price",)}),
        ("Teachers", {"fields": ("teacher_slugs",)}),
        (
            "Presentation",
            {"fields": ("accent_color", "badge", "order", "is_featured", "is_published")},
        ),
    )

    def get_changeform_initial_data(self, request):
        # A new course starts with every teacher ticked; untick as needed.
        initial = super().get_changeform_initial_data(request)
        initial.setdefault("teacher_slugs", [teacher.slug for teacher in TEACHERS])
        return initial

    @admin.display(description="Price", ordering="price")
    def price_display(self, obj):
        return money(obj.price, obj.currency)

    @admin.display(description="Duration")
    def duration_display(self, obj):
        return f"{obj.duration_weeks} wks · {obj.total_hours:g} h"
