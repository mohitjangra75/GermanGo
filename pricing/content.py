"""Pricing plans.

A plan is how the school packages its teaching. Courses carry their own
total price; plans are the headline bundles a visitor compares before
enquiring. The slug identifies the plan an enquiry was about, and
``course_slugs`` name courses as they are set in the admin.
"""

from __future__ import annotations

from dataclasses import dataclass, field

PERIODS = {
    "hour": "per hour",
    "week": "per week",
    "month": "per month",
    "course": "per course",
}


@dataclass(frozen=True)
class Feature:
    """One line in a plan's comparison list; excluded lines are struck through."""

    text: str
    is_included: bool = True


@dataclass(frozen=True)
class Plan:
    slug: str
    name: str
    price: int
    tagline: str = ""
    description: str = ""
    currency: str = "INR"
    period: str = "course"
    price_note: str = ""
    class_size: str = ""
    hours_included: str = ""
    course_slugs: list[str] = field(default_factory=list)
    features: list[Feature] = field(default_factory=list)
    cta_label: str = "Enquire about this plan"
    is_featured: bool = False
    badge: str = ""
    accent_color: str = "#9B2226"

    def __str__(self) -> str:
        return self.name

    def get_period_display(self) -> str:
        return PERIODS[self.period]


PLANS = [
    Plan(
        slug="a1-a2-together",
        name="A1 + A2 Together",
        price=10999,
        tagline="Best value for beginners.",
        description="The two beginner levels booked together, from your first Hallo "
        "to handling an ordinary day in German. Saves ₹1,001 against booking them "
        "separately.",
        price_note="Both levels · saves ₹1,001 against separate booking",
        class_size="Maximum 8 per batch",
        hours_included="3 hours a week, 20 weeks",
        badge="Best for beginners",
        accent_color="#B98600",
        cta_label="Enquire about A1 + A2",
        course_slugs=["german-a1-beginner-level", "german-a2-elementary-level"],
        features=[
            Feature("Both levels, one enrolment"),
            Feature("Same teacher across both"),
            Feature("Course materials included"),
            Feature("Free placement conversation"),
            Feature("Certificate after each level"),
            Feature("Goethe / telc exam coaching", is_included=False),
        ],
    ),
    Plan(
        slug="b1-b2-together",
        name="B1 + B2 Together",
        price=14999,
        tagline="Take your skills to the next level.",
        description="The two intermediate levels booked together — the pair that "
        "takes you from getting by to genuinely work-ready. Saves ₹1,001 against "
        "booking separately.",
        price_note="Both levels · saves ₹1,001 against separate booking",
        class_size="Maximum 8 per batch",
        hours_included="3–3.5 hours a week, 24 weeks",
        badge="Next level",
        accent_color="#2F5D8C",
        cta_label="Enquire about B1 + B2",
        course_slugs=["german-b1-intermediate-level", "german-b2-upper-intermediate-level"],
        features=[
            Feature("Both levels, one enrolment"),
            Feature("Career and study ready by the end"),
            Feature("Course materials included"),
            Feature("Free placement conversation"),
            Feature("Certificate after each level"),
            Feature("Goethe / telc exam coaching", is_included=False),
        ],
    ),
    Plan(
        slug="a1-to-b2-all-levels",
        name="A1 to B2 — All Levels",
        price=24599,
        tagline="The complete German learning journey.",
        description="Every level from absolute beginner to upper intermediate, booked "
        "as one journey with one teacher team following you the whole way. Saves "
        "₹3,401 against booking level by level.",
        price_note="All four levels · saves ₹3,401 against separate booking",
        class_size="Maximum 8 per batch",
        hours_included="3–3.5 hours a week, 44 weeks",
        badge="Complete journey",
        is_featured=True,
        accent_color="#C0261A",
        cta_label="Enquire about the full journey",
        course_slugs=[
            "german-a1-beginner-level",
            "german-a2-elementary-level",
            "german-b1-intermediate-level",
            "german-b2-upper-intermediate-level",
        ],
        features=[
            Feature("All four levels, one enrolment"),
            Feature("A single plan from beginner to B2"),
            Feature("Course materials included"),
            Feature("Free placement conversation"),
            Feature("Certificate after each level"),
            Feature("Priority place in the next batch"),
        ],
    ),
]


def get_plan(slug: str | None) -> Plan | None:
    return next((plan for plan in PLANS if plan.slug == slug), None)


def plans_covering(course) -> list[Plan]:
    return [plan for plan in PLANS if course.slug in plan.course_slugs]
