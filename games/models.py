"""The Germany map quiz.

A light interactive that gives visitors a reason to stay on the site and a
natural bridge into an enquiry. Cities are managed in the admin; plays are
recorded anonymously so the school can see whether it is worth keeping.
"""

from django.db import models

from core.models import PublishableModel, SlugModel, TimeStampedModel


class MapCity(TimeStampedModel, SlugModel, PublishableModel):
    """A city on the 3D map of Germany."""

    slug_source_field = "name"

    name = models.CharField(max_length=80, unique=True)
    state = models.CharField(max_length=80, blank=True, help_text="Bundesland.")
    # Normalised map coordinates: x runs -1 (west) to 1 (east),
    # z runs -1 (north) to 1 (south).
    map_x = models.FloatField(help_text="-1 (west) to 1 (east).")
    map_z = models.FloatField(help_text="-1 (north) to 1 (south).")

    hint = models.CharField(
        max_length=160,
        blank=True,
        help_text='Shown if the player asks. e.g. "In the far north, on the Elbe."',
    )
    fun_fact = models.CharField(
        max_length=240, blank=True, help_text="Shown after a correct answer."
    )
    german_phrase = models.CharField(
        max_length=120, blank=True, help_text="A phrase associated with this city."
    )
    german_phrase_en = models.CharField(max_length=140, blank=True)
    population = models.PositiveIntegerField(blank=True, null=True)
    accent_color = models.CharField(max_length=7, default="#C0261A")
    difficulty = models.PositiveSmallIntegerField(
        default=1,
        choices=[(1, "Easy — well known"), (2, "Medium"), (3, "Hard — smaller city")],
    )
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "map city"
        verbose_name_plural = "map cities"

    def __str__(self) -> str:
        return self.name

    def as_payload(self) -> dict:
        """The compact shape the Three.js scene and the quiz need."""
        return {
            "slug": self.slug,
            "name": self.name,
            "state": self.state,
            "x": self.map_x,
            "z": self.map_z,
            "color": self.accent_color,
            "hint": self.hint,
            "fact": self.fun_fact,
            "phrase": self.german_phrase,
            "phraseEn": self.german_phrase_en,
            "difficulty": self.difficulty,
        }


class GamePlay(TimeStampedModel):
    """One completed round. No personal data — just whether people play."""

    class Game(models.TextChoices):
        MAP_QUIZ = "map_quiz", "Germany map quiz"

    game = models.CharField(max_length=20, choices=Game.choices, default=Game.MAP_QUIZ)
    score = models.PositiveSmallIntegerField(default=0)
    total = models.PositiveSmallIntegerField(default=0)
    seconds = models.PositiveIntegerField(default=0)
    used_hints = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "game play"
        verbose_name_plural = "game plays"
        indexes = [models.Index(fields=["game", "-created_at"])]

    def __str__(self) -> str:
        return f"{self.get_game_display()} — {self.score}/{self.total}"

    @property
    def percent(self) -> int:
        return round(self.score * 100 / self.total) if self.total else 0

    @property
    def verdict(self) -> str:
        """The headline shown on the result card."""
        percent = self.percent
        if percent == 100:
            return "Perfekt!"
        if percent >= 80:
            return "Sehr gut!"
        if percent >= 60:
            return "Nicht schlecht!"
        if percent >= 40:
            return "Ganz okay."
        return "Übung macht den Meister."
