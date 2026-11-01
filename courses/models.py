"""Course offerings, managed in the admin.

These describe what the school *sells* — level, format, duration, syllabus
outline and price — not lesson content. There is no learner-facing course
software here; the goal of every course page is an enquiry.
"""

from django.db import models
from django.urls import reverse

from core.models import TimeStampedModel
from teachers.content import get_teacher

CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]


def split_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


class CourseQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)


class Course(TimeStampedModel):
    class Format(models.TextChoices):
        GROUP = "group", "Small group"
        PRIVATE = "private", "One to one"
        INTENSIVE = "intensive", "Intensive"
        CORPORATE = "corporate", "Corporate / in-company"
        EXAM = "exam", "Exam preparation"

    class Delivery(models.TextChoices):
        ONLINE = "online", "Online"
        IN_PERSON = "in_person", "In person"
        HYBRID = "hybrid", "Online or in person"

    title = models.CharField(max_length=140)
    slug = models.SlugField(
        max_length=180,
        unique=True,
        help_text="The course's URL. Changing it breaks existing links.",
    )
    level_code = models.CharField(
        max_length=4, choices=[(code, code) for code in CEFR_LEVELS], default="A1"
    )
    subtitle = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    audience = models.TextField(
        "who it is for", blank=True, help_text="One line per audience; rendered as a list."
    )
    outcomes = models.TextField(
        blank=True, help_text="One 'you will be able to…' per line."
    )

    course_format = models.CharField(
        max_length=12, choices=Format.choices, default=Format.GROUP
    )
    delivery = models.CharField(
        max_length=12, choices=Delivery.choices, default=Delivery.ONLINE
    )
    duration_weeks = models.PositiveSmallIntegerField(default=10)
    hours_per_week = models.DecimalField(max_digits=4, decimal_places=1, default=3)
    max_class_size = models.PositiveSmallIntegerField(
        default=8, help_text="Set to 1 for one-to-one courses."
    )
    schedule_note = models.CharField(
        max_length=160, blank=True, help_text='e.g. "Flexible timings (IST)".'
    )
    next_start_date = models.DateField(
        blank=True, null=True, help_text="Leave blank until a batch is scheduled."
    )

    price = models.PositiveIntegerField(
        default=0, help_text="Total fee for the course in rupees. 0 shows “On request”."
    )
    currency = models.CharField(max_length=3, default="INR")
    teacher_slugs = models.JSONField("teachers", default=list, blank=True)

    accent_color = models.CharField(max_length=7, default="#9B2226")
    badge = models.CharField(
        max_length=30, blank=True, help_text='Optional flag on the card, e.g. "Most popular".'
    )
    is_featured = models.BooleanField(
        default=False, help_text="Featured courses appear on the homepage."
    )
    is_published = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    objects = CourseQuerySet.as_manager()

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("courses:detail", kwargs={"slug": self.slug})

    @property
    def audience_list(self) -> list[str]:
        return split_lines(self.audience)

    @property
    def outcome_list(self) -> list[str]:
        return split_lines(self.outcomes)

    @property
    def teachers(self) -> list:
        return [t for t in map(get_teacher, self.teacher_slugs) if t]

    @property
    def total_hours(self) -> float:
        return round(float(self.hours_per_week) * self.duration_weeks, 1)

    @property
    def price_per_hour(self):
        hours = self.total_hours
        if not hours or not self.price:
            return None
        return round(float(self.price) / hours, 2)

    @property
    def is_one_to_one(self) -> bool:
        return self.max_class_size <= 1


class CourseModule(models.Model):
    """One block of the published syllabus outline."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    week_range = models.CharField(
        max_length=40, blank=True, help_text='e.g. "Weeks 1–2".'
    )
    title = models.CharField(max_length=140)
    summary = models.CharField(max_length=300, blank=True)
    topics = models.TextField(blank=True, help_text="One topic per line; rendered as a list.")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "syllabus module"

    def __str__(self) -> str:
        return self.title

    @property
    def topic_list(self) -> list[str]:
        return split_lines(self.topics)
