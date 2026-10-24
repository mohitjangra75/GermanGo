"""Shared abstract models plus the small site-wide content models."""

from django.db import models
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SlugModel(models.Model):
    """Auto-slugs from ``slug_source_field`` when the slug is left blank."""

    slug_source_field = "title"

    slug = models.SlugField(max_length=180, unique=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(getattr(self, self.slug_source_field, "") or "item")[:170]
            candidate, suffix = base, 2
            model = self.__class__
            while model.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base[:170 - len(str(suffix)) - 1]}-{suffix}"
                suffix += 1
            self.slug = candidate
        super().save(*args, **kwargs)


class SeoModel(models.Model):
    """Per-page SEO overrides; views fall back to sensible defaults."""

    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=165, blank=True)
    og_image = models.ImageField(upload_to="og/", blank=True, null=True)
    noindex = models.BooleanField(default=False)

    class Meta:
        abstract = True


class PublishedQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)


class PublishableModel(models.Model):
    is_published = models.BooleanField(default=True, db_index=True)

    objects = PublishedQuerySet.as_manager()

    class Meta:
        abstract = True


# ---------------------------------------------------------------------------
# Site content, all editable in the admin
# ---------------------------------------------------------------------------


class Testimonial(TimeStampedModel):
    """Social proof for the homepage and the courses page."""

    name = models.CharField(max_length=80)
    role = models.CharField(max_length=120, blank=True)
    level_reached = models.CharField(
        max_length=40, blank=True, help_text='e.g. "Reached B1 in 7 months".'
    )
    quote = models.TextField(max_length=420)
    avatar = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="testimonials",
        help_text="Show this quote on a specific course page too.",
    )
    rating = models.PositiveSmallIntegerField(
        default=5, choices=[(n, f"{n} stars") for n in range(1, 6)]
    )
    order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.name} — {self.level_reached or 'student'}"

    @property
    def star_range(self) -> range:
        return range(self.rating)


class SiteStat(models.Model):
    """Headline numbers in the social-proof band."""

    label = models.CharField(max_length=60)
    value = models.CharField(max_length=24)
    caption = models.CharField(max_length=120, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return f"{self.value} {self.label}"


class ProcessStep(models.Model):
    """One step of "how it works", shown on the homepage and Process page."""

    number = models.CharField(max_length=4, help_text='e.g. "01".')
    title = models.CharField(max_length=120)
    body = models.TextField(max_length=600)
    icon = models.CharField(
        max_length=40, default="compass", help_text="Name of an inline SVG icon."
    )
    detail = models.TextField(
        blank=True,
        max_length=900,
        help_text="Longer text shown only on the Process page.",
    )
    order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "process step"

    def __str__(self) -> str:
        return f"{self.number}. {self.title}"


class Faq(models.Model):
    """A question and answer, optionally scoped to one page."""

    class Page(models.TextChoices):
        HOME = "home", "Homepage"
        COURSES = "courses", "Courses"
        PRICING = "pricing", "Pricing"
        TEACHERS = "teachers", "Teachers"
        PROCESS = "process", "How it works"
        ENQUIRY = "enquiry", "Enquiry"

    page = models.CharField(max_length=12, choices=Page.choices, default=Page.HOME)
    question = models.CharField(max_length=200)
    answer = models.TextField(max_length=900)
    order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["page", "order", "id"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self) -> str:
        return self.question


class Highlight(models.Model):
    """Short selling points, grouped by where they appear.

    Covers both the thin band of reassurances under the hero and the
    "Opportunities after learning German" list, which share a shape.
    """

    class Section(models.TextChoices):
        TRUST = "trust", "Trust strip — short labels under the hero"
        OPPORTUNITY = "opportunity", "Opportunities after learning German"
        COURSE_PERK = "course_perk", "Course perks — shown on the courses page"

    section = models.CharField(
        max_length=16, choices=Section.choices, default=Section.TRUST
    )
    title = models.CharField(max_length=120)
    description = models.CharField(
        max_length=240, blank=True, help_text="Left blank for trust-strip labels."
    )
    icon = models.CharField(
        max_length=40, default="check", help_text="Name of an inline SVG icon."
    )
    accent_color = models.CharField(max_length=7, default="#C0261A")
    order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["section", "order", "id"]

    def __str__(self) -> str:
        return f"{self.get_section_display()}: {self.title}"


class HeroWord(models.Model):
    """A German word floating in the homepage 3D scene.

    Purely decorative brand dressing — clicking one shows its translation,
    which is what makes the hero feel like a language school rather than a
    stock illustration.
    """

    word = models.CharField(max_length=60, unique=True)
    article = models.CharField(
        max_length=12, blank=True, help_text="der / die / das, when relevant."
    )
    translation = models.CharField(max_length=120)
    example_de = models.CharField(max_length=200, blank=True)
    example_en = models.CharField(max_length=200, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "word"]
        verbose_name = "hero word"

    def __str__(self) -> str:
        return self.display_word

    @property
    def display_word(self) -> str:
        return f"{self.article} {self.word}".strip()
