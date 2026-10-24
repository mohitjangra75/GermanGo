"""Pricing plans.

A plan is how the school packages its teaching — group seat, private hour,
intensive week. Courses carry their own total price; plans are the headline
options a visitor compares before enquiring.
"""

from django.db import models

from core.models import PublishableModel, TimeStampedModel


class Plan(TimeStampedModel, PublishableModel):
    class Period(models.TextChoices):
        HOUR = "hour", "per hour"
        WEEK = "week", "per week"
        MONTH = "month", "per month"
        COURSE = "course", "per course"

    name = models.CharField(max_length=80)
    tagline = models.CharField(max_length=160, blank=True)
    description = models.TextField(blank=True, max_length=600)

    price = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default="INR")
    period = models.CharField(max_length=8, choices=Period.choices, default=Period.MONTH)
    price_note = models.CharField(
        max_length=120, blank=True, help_text='e.g. "Billed per 10-week block".'
    )

    class_size = models.CharField(
        max_length=60, blank=True, help_text='e.g. "Up to 8 students" or "One to one".'
    )
    hours_included = models.CharField(
        max_length=60, blank=True, help_text='e.g. "3 hours a week".'
    )

    courses = models.ManyToManyField(
        "courses.Course",
        blank=True,
        related_name="plans",
        help_text="Courses this plan covers. Shown on those course pages.",
    )

    cta_label = models.CharField(max_length=40, default="Enquire about this plan")
    is_featured = models.BooleanField(
        default=False, help_text="Highlights the plan as the recommended option."
    )
    badge = models.CharField(
        max_length=30, blank=True, help_text='e.g. "Most popular".'
    )
    accent_color = models.CharField(max_length=7, default="#9B2226")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "price"]

    def __str__(self) -> str:
        return f"{self.name} — {self.currency} {self.price:.0f} {self.get_period_display()}"

    @property
    def included_features(self):
        return self.features.filter(is_included=True)


class PlanFeature(models.Model):
    """One line in a plan's comparison list."""

    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="features")
    text = models.CharField(max_length=140)
    is_included = models.BooleanField(
        default=True, help_text="Uncheck to show the line struck through."
    )
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "plan feature"

    def __str__(self) -> str:
        return self.text
