from django.contrib import admin

from .models import Plan, PlanFeature


class PlanFeatureInline(admin.TabularInline):
    model = PlanFeature
    extra = 4
    fields = ("order", "text", "is_included")
    ordering = ("order",)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price_display",
        "class_size",
        "hours_included",
        "badge",
        "is_featured",
        "order",
        "is_published",
    )
    list_editable = ("order", "is_featured", "is_published")
    list_filter = ("is_published", "is_featured", "period")
    search_fields = ("name", "tagline", "description")
    filter_horizontal = ("courses",)
    inlines = [PlanFeatureInline]
    save_on_top = True

    fieldsets = (
        (None, {"fields": ("name", "tagline", "description")}),
        ("Price", {"fields": (("price", "currency", "period"), "price_note")}),
        ("What's included", {"fields": ("class_size", "hours_included", "courses")}),
        (
            "Presentation",
            {"fields": ("cta_label", "badge", "is_featured", "accent_color", "order", "is_published")},
        ),
    )

    @admin.display(description="Price", ordering="price")
    def price_display(self, obj):
        from core.templatetags.germango import money

        return f"{money(obj.price, obj.currency)} {obj.get_period_display()}"
