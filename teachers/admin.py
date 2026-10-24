from django.contrib import admin
from django.utils.html import format_html

from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = (
        "thumb",
        "name",
        "role",
        "levels_taught",
        "years_experience",
        "is_accepting_students",
        "is_featured",
        "is_published",
    )
    list_display_links = ("thumb", "name")
    list_editable = ("is_accepting_students", "is_featured", "is_published")
    list_filter = ("is_published", "is_featured", "is_accepting_students", "is_native_speaker")
    search_fields = ("name", "role", "headline", "bio", "specialisms")
    save_on_top = True

    fieldsets = (
        (None, {"fields": ("name", "role", "photo", "headline")}),
        ("Profile", {"fields": ("bio", "home_city", "is_native_speaker", "years_experience")}),
        (
            "Teaching",
            {
                "fields": ("languages", "levels_taught", "specialisms", "qualifications"),
                "description": "Languages and levels are comma separated. "
                "Specialisms and qualifications take one item per line.",
            },
        ),
        (
            "Display",
            {"fields": ("is_accepting_students", "is_featured", "order", "is_published")},
        ),
        (
            "SEO",
            {
                "classes": ("collapse",),
                "fields": ("slug", "seo_title", "seo_description", "og_image", "noindex"),
            },
        ),
    )

    @admin.display(description="")
    def thumb(self, obj):
        if not obj.photo:
            return format_html(
                '<span style="display:inline-grid;place-items:center;width:34px;'
                'height:34px;border-radius:50%;background:#eee;font-size:11px;'
                'font-weight:700">{}</span>',
                obj.initials,
            )
        return format_html(
            '<img src="{}" style="width:34px;height:34px;border-radius:50%;'
            'object-fit:cover">',
            obj.photo.url,
        )
