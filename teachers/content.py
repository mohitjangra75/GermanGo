"""Teacher profiles — the strongest trust signal on a language-school site.

Edit the profile here and redeploy. A photo is a path under ``static/``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from django.templatetags.static import static
from django.urls import reverse


@dataclass(frozen=True)
class Teacher:
    slug: str
    name: str
    role: str = ""
    photo: str = ""
    headline: str = ""
    bio: str = ""
    is_native_speaker: bool = True
    home_city: str = ""
    years_experience: int = 1
    languages: list[str] = field(default_factory=list)
    levels: list[str] = field(default_factory=list)
    specialisms: list[str] = field(default_factory=list)
    qualifications: list[str] = field(default_factory=list)
    is_accepting_students: bool = True
    is_featured: bool = False

    def get_absolute_url(self) -> str:
        return reverse("teachers:detail", kwargs={"slug": self.slug})

    @property
    def photo_url(self) -> str:
        return static(self.photo) if self.photo else ""

    @property
    def initials(self) -> str:
        parts = self.name.split()
        if not parts:
            return "?"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()


# The school is one person. A real, named teacher: the experience and
# certification here are the ones she supplied, and nothing beyond them is
# invented. The rest describes only what the published catalogue commits to.
TEACHERS = [
    Teacher(
        slug="jaishree-mudgal",
        name="Jaishree Mudgal",
        role="Founder & German teacher",
        photo="images/teachers/jaishree-mudgal.jpg",
        headline="Teaches every level from A1 to B2, in small live online batches "
        "on IST timings.",
        bio="I teach German to adults across India — complete beginners through to "
        "B2, plus Goethe and telc exam preparation.\n\n"
        "Batches stay small, capped at eight, so everybody speaks in every session. "
        "Classes run live over video on IST timings, which means no recordings to "
        "fall behind on and no awkward 3am European slots.\n\n"
        "Before you book anything we have a short placement conversation, free and "
        "with no obligation, so you start at the right level rather than guessing.",
        is_native_speaker=False,
        home_city="India · teaches on IST timings",
        years_experience=5,
        languages=["German", "English", "Hindi"],
        levels=["A1", "A2", "B1", "B2"],
        specialisms=[
            "Complete beginners starting from zero",
            "Goethe examination preparation",
            "telc examination preparation",
            "Small-batch live online teaching",
        ],
        qualifications=["C1 certified in German"],
        is_featured=True,
    ),
]


def get_teacher(slug: str | None) -> Teacher | None:
    return next((teacher for teacher in TEACHERS if teacher.slug == slug), None)
