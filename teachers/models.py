"""Teacher profiles — the strongest trust signal on a language-school site."""

from django.db import models
from django.urls import reverse

from core.models import PublishableModel, SeoModel, SlugModel, TimeStampedModel


class Teacher(TimeStampedModel, SlugModel, SeoModel, PublishableModel):
    slug_source_field = "name"

    name = models.CharField(max_length=120)
    role = models.CharField(
        max_length=120, blank=True, help_text='e.g. "Senior tutor, exam preparation".'
    )
    photo = models.ImageField(upload_to="teachers/", blank=True, null=True)
    headline = models.CharField(
        max_length=200, blank=True, help_text="One sentence shown on the card."
    )
    bio = models.TextField(blank=True)

    is_native_speaker = models.BooleanField(default=True)
    home_city = models.CharField(max_length=80, blank=True)
    years_experience = models.PositiveSmallIntegerField(default=1)
    languages = models.CharField(
        max_length=200, blank=True, help_text="Comma separated, e.g. German, English, Spanish."
    )
    levels_taught = models.CharField(
        max_length=60,
        blank=True,
        help_text="Comma separated CEFR codes, e.g. A1, A2, B1.",
    )
    specialisms = models.TextField(
        blank=True, help_text="One specialism per line, e.g. Goethe exam preparation."
    )
    qualifications = models.TextField(
        blank=True, help_text="One qualification per line."
    )

    is_accepting_students = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("teachers:detail", kwargs={"slug": self.slug})

    @property
    def language_list(self) -> list[str]:
        return [item.strip() for item in self.languages.split(",") if item.strip()]

    @property
    def level_list(self) -> list[str]:
        return [item.strip() for item in self.levels_taught.split(",") if item.strip()]

    @property
    def specialism_list(self) -> list[str]:
        return [line.strip() for line in self.specialisms.splitlines() if line.strip()]

    @property
    def qualification_list(self) -> list[str]:
        return [line.strip() for line in self.qualifications.splitlines() if line.strip()]

    @property
    def initials(self) -> str:
        parts = self.name.split()
        if not parts:
            return "?"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()
