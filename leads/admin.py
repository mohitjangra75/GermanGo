"""The enquiry inbox — where the school actually works."""

import csv

from django.contrib import admin, messages
from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html

from .models import Enquiry


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "contact_links",
        "interest",
        "status_badge",
        "age",
        "created_at",
    )
    list_filter = ("status", "created_at", "course", "plan", "teacher")
    search_fields = ("name", "email", "phone", "message", "internal_notes")
    date_hierarchy = "created_at"
    list_per_page = 40
    actions = ["mark_contacted", "mark_qualified", "mark_enrolled", "mark_spam", "export_csv"]
    save_on_top = True

    readonly_fields = (
        "name",
        "email",
        "phone",
        "message",
        "course",
        "plan",
        "teacher",
        "source_path",
        "referrer",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "The enquiry",
            {
                "fields": ("name", "email", "phone", "message"),
                "description": "Submitted by the visitor. Read-only so the record "
                "of what they actually wrote stays intact.",
            },
        ),
        (
            "Where it came from",
            {"fields": (("course", "plan", "teacher"), "source_path", "referrer")},
        ),
        (
            "Follow up",
            {"fields": ("status", "contacted_at", "internal_notes")},
        ),
        ("Timestamps", {"classes": ("collapse",), "fields": ("created_at", "updated_at")}),
    )

    def has_add_permission(self, request):
        # Enquiries only ever arrive through the public form.
        return False

    # --- Columns -----------------------------------------------------------

    @admin.display(description="Contact")
    def contact_links(self, obj):
        # Phone first: it is the required field, and how the school follows up.
        if obj.phone and obj.email:
            return format_html(
                '<a href="tel:{0}">{0}</a><br><a href="mailto:{1}">{1}</a>',
                obj.phone,
                obj.email,
            )
        if obj.phone:
            return format_html('<a href="tel:{0}">{0}</a>', obj.phone)
        return format_html('<a href="mailto:{0}">{0}</a>', obj.email)

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        colours = {
            "new": "#9B2226",
            "contacted": "#C99700",
            "qualified": "#2F5D8C",
            "enrolled": "#2A6F52",
            "lost": "#77726A",
            "spam": "#A9A399",
        }
        return format_html(
            '<b style="color:{}">{}</b>', colours.get(obj.status, "#333"), obj.get_status_display()
        )

    @admin.display(description="Waiting", ordering="created_at")
    def age(self, obj):
        if obj.status != Enquiry.Status.NEW:
            return "—"
        hours = (timezone.now() - obj.created_at).total_seconds() / 3600
        if hours < 1:
            return format_html('<b style="color:#2A6F52">just now</b>')
        if hours < 24:
            return f"{int(hours)} h"
        days = int(hours // 24)
        colour = "#9B2226" if days >= 2 else "#C99700"
        return format_html('<b style="color:{}">{} d</b>', colour, days)

    # --- Bulk actions ------------------------------------------------------

    def _set_status(self, request, queryset, status, label):
        updates = {"status": status}
        if status == Enquiry.Status.CONTACTED:
            updates["contacted_at"] = timezone.now()
        count = queryset.update(**updates)
        self.message_user(
            request, f"{count} enquir{'y' if count == 1 else 'ies'} marked {label}.",
            messages.SUCCESS,
        )

    @admin.action(description="Mark as contacted")
    def mark_contacted(self, request, queryset):
        self._set_status(request, queryset, Enquiry.Status.CONTACTED, "contacted")

    @admin.action(description="Mark as qualified")
    def mark_qualified(self, request, queryset):
        self._set_status(request, queryset, Enquiry.Status.QUALIFIED, "qualified")

    @admin.action(description="Mark as enrolled")
    def mark_enrolled(self, request, queryset):
        self._set_status(request, queryset, Enquiry.Status.ENROLLED, "enrolled")

    @admin.action(description="Mark as spam")
    def mark_spam(self, request, queryset):
        self._set_status(request, queryset, Enquiry.Status.SPAM, "spam")

    @admin.action(description="Export selected to CSV")
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        stamp = timezone.now().date().isoformat()
        response["Content-Disposition"] = f'attachment; filename="enquiries-{stamp}.csv"'

        writer = csv.writer(response)
        writer.writerow(
            ["Received", "Name", "Email", "Phone", "Interest", "Status", "Message", "Source"]
        )
        for enquiry in queryset.select_related("course", "plan", "teacher"):
            writer.writerow(
                [
                    enquiry.created_at.strftime("%Y-%m-%d %H:%M"),
                    enquiry.name,
                    enquiry.email,
                    enquiry.phone,
                    enquiry.interest,
                    enquiry.get_status_display(),
                    enquiry.message,
                    enquiry.source_path,
                ]
            )
        return response
