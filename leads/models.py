"""Enquiry capture — the conversion goal of every page."""

from django.db import models
from django.utils import timezone

from core.models import TimeStampedModel


class Enquiry(TimeStampedModel):
    """One lead. Captured with four fields; qualified in the admin."""

    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        QUALIFIED = "qualified", "Qualified"
        ENROLLED = "enrolled", "Enrolled"
        LOST = "lost", "Not proceeding"
        SPAM = "spam", "Spam"

    # --- What the visitor typed -------------------------------------------
    name = models.CharField(max_length=120)
    # Phone is the required contact detail; the school follows up by call
    # or WhatsApp. Email is optional.
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40)
    message = models.TextField(max_length=2000, blank=True)

    # --- Context captured automatically -----------------------------------
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="enquiries",
        help_text="Set when the form was submitted from a course page.",
    )
    plan = models.ForeignKey(
        "pricing.Plan",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="enquiries",
    )
    teacher = models.ForeignKey(
        "teachers.Teacher",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="enquiries",
    )
    source_path = models.CharField(
        max_length=300, blank=True, help_text="The page the enquiry came from."
    )
    referrer = models.CharField(max_length=300, blank=True)

    # --- Sales workflow ----------------------------------------------------
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.NEW, db_index=True
    )
    internal_notes = models.TextField(
        blank=True, help_text="Private. Never shown to the enquirer."
    )
    contacted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "enquiry"
        verbose_name_plural = "enquiries"
        indexes = [models.Index(fields=["status", "-created_at"])]

    def __str__(self) -> str:
        return f"{self.name} <{self.phone or self.email}>"

    @property
    def is_new(self) -> bool:
        return self.status == self.Status.NEW

    @property
    def interest(self) -> str:
        """A short label for what the lead asked about."""
        if self.course:
            return f"Course: {self.course.title}"
        if self.plan:
            return f"Plan: {self.plan.name}"
        if self.teacher:
            return f"Teacher: {self.teacher.name}"
        return "General enquiry"

    def mark_contacted(self) -> None:
        self.status = self.Status.CONTACTED
        self.contacted_at = self.contacted_at or timezone.now()
        self.save(update_fields=["status", "contacted_at", "updated_at"])
