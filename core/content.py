"""Site-wide copy: everything on the site that is not a course, plan,
teacher or map city.

Edit the lists here and redeploy. Order in each list is display order, and
an ``icon`` is a name from ``templates/components/icon.html``.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HeroWord:
    """A German word floating in the homepage 3D scene."""

    article: str
    word: str
    translation: str
    example_de: str = ""
    example_en: str = ""

    @property
    def display_word(self) -> str:
        return f"{self.article} {self.word}".strip()


@dataclass(frozen=True)
class Highlight:
    """A short selling point: a trust-strip label or an opportunity card."""

    title: str
    icon: str
    description: str = ""
    accent_color: str = "#C0261A"


@dataclass(frozen=True)
class ProcessStep:
    number: str
    title: str
    icon: str
    body: str
    # Longer text shown only on the How it works page.
    detail: str = ""


@dataclass(frozen=True)
class Stat:
    value: str
    label: str
    caption: str = ""


@dataclass(frozen=True)
class Testimonial:
    name: str
    quote: str
    role: str = ""
    level_reached: str = ""
    rating: int = 5
    # A course slug, to show the quote on that course page too.
    course: str = ""

    @property
    def star_range(self) -> range:
        return range(self.rating)


@dataclass(frozen=True)
class Faq:
    question: str
    answer: str


# Decorative brand dressing — clicking one shows its translation. Eight or
# so is plenty.
HERO_WORDS = [
    HeroWord("", "Hallo", "Hello", "Hallo, ich heiße Anna.", "Hello, my name is Anna."),
    HeroWord("", "Danke", "Thank you", "Danke für Ihre Hilfe!", "Thank you for your help!"),
    HeroWord("", "Guten Morgen", "Good morning", "Guten Morgen, Herr Weber.",
             "Good morning, Mr Weber."),
    HeroWord("der", "Bahnhof", "train station", "Wo ist der Bahnhof?",
             "Where is the train station?"),
    HeroWord("der", "Freund", "friend", "Er ist mein bester Freund.", "He is my best friend."),
    HeroWord("die", "Familie", "family", "Meine Familie wohnt in Köln.",
             "My family lives in Cologne."),
    HeroWord("das", "Haus", "house", "Das Haus ist groß.", "The house is big."),
    HeroWord("die", "Arbeit", "work", "Ich gehe um acht zur Arbeit.", "I go to work at eight."),
]

# The reassurance band under the hero.
TRUST_POINTS = [
    Highlight("Flexible Learning", "laptop", "Live online batches, flexible timings"),
    Highlight("Expert Guidance", "users", "C1-certified teacher, 5 years' experience"),
    Highlight("Structured Curriculum", "layers", "A clear path from A1 to B2"),
    Highlight("Lifetime Access", "shield", "Keep your materials and recordings"),
]

# "Opportunities after learning German" — the reason people enrol.
OPPORTUNITIES = [
    Highlight("Study in Germany", "graduation",
              "Get admission to top universities with German language skills.", "#B98600"),
    Highlight("Better Job Opportunities", "briefcase",
              "Work in MNCs, German companies or global firms.", "#2A6F52"),
    Highlight("Travel the World", "plane",
              "Explore Germany and other European countries easily.", "#C0261A"),
    Highlight("Connect with People", "users",
              "Make new friends and experience different cultures.", "#2F5D8C"),
    Highlight("A Brighter Future", "trending",
              "Build a global career and open doors to more opportunities.", "#7A4B9C"),
]

PROCESS_STEPS = [
    ProcessStep(
        "01", "Tell us where you are", "compass",
        "Send a short message — your name, roughly your level and what you want German "
        "for. You do not need to know your CEFR level; most people don't.",
        "There is no form to fill in beyond four fields, and no obligation. If you "
        "would rather phone, the number is at the top of every page.",
    ),
    ProcessStep(
        "02", "A free placement chat", "chat",
        "We book a fifteen-minute conversation, half in English and half in German. "
        "It tells us far more than a written test would.",
        "It is genuinely a conversation, not an exam. We are listening for what you "
        "can already do, not counting your mistakes. At the end we tell you which "
        "level you belong in — even if that means a course we are not currently "
        "running.",
    ),
    ProcessStep(
        "03", "We match a course and a teacher", "users",
        "You get a specific recommendation: this course, this teacher, this start "
        "date, this price. If nothing fits, we say so.",
        "Teachers are matched on more than level. Someone preparing for a B2 exam in "
        "six weeks needs a different person from someone learning German for the "
        "pleasure of it, and we will explain why we picked who we picked.",
    ),
    ProcessStep(
        "04", "Start, and keep going", "sparkle",
        "Lessons begin. You are reviewed every few weeks, and moved up when you are "
        "ready rather than when the calendar says so.",
        "If a course turns out to be wrong for you, tell us within the first two "
        "sessions and we will move you to a batch that fits better. Fees are "
        "non-refundable, which is why the placement chat comes first.",
    ),
]

# Structural facts only. Anything like "2,400 students taught" or a
# pass-rate percentage would be an unverifiable claim on a live site, so add
# those once there are real figures behind them.
STATS = [
    Stat("A1–B2", "Levels taught", "Plus Goethe & telc preparation"),
    Stat("8", "Maximum batch size", "Usually runs with six"),
    Stat("₹6,000", "Courses from", "For a full 10-week level"),
    Stat("< 1 day", "Reply time", "Usually the same morning"),
]

# Genuine student quotes only — publishing invented ones under invented
# names would be misleading. Shown on the homepage, the courses page and
# the pricing page; ``course`` also puts a quote on that course's page.
TESTIMONIALS = [
    Testimonial(
        "Ananya Sharma",
        "GermanGo made learning German so structured and manageable alongside my "
        "job. The batch size is small, which means I got plenty of opportunities to "
        "speak and clear my doubts directly with the teacher.",
        role="Working Professional",
        level_reached="Reached B1 in 6 months",
    ),
    Testimonial(
        "Rahul Verma",
        "I needed my B2 certificate for my studies abroad. The focused exam "
        "preparation modules and personal attention at GermanGo gave me the exact "
        "confidence I needed to pass on my first attempt.",
        role="Master’s student in Germany",
        level_reached="Cleared Goethe B2 exam",
        course="german-b2-exam-preparation-goethe-telc",
    ),
    Testimonial(
        "Priya Nair",
        "Starting from absolute zero was intimidating, but the interactive lessons "
        "and friendly teaching style at GermanGo made it fun. The IST evening "
        "timings worked out perfectly for my schedule.",
        role="Language enthusiast",
        level_reached="Completed A2 level",
    ),
]

FAQS = {
    "home": [
        Faq("What levels of German do you teach and how large are the batches?",
            "We offer live online German courses from level A1 to B2, as well as Goethe "
            "and telc exam preparation. To ensure personal attention and interactive "
            "speaking practice, our groups are kept small with a maximum of 8 students "
            "per batch."),
        Faq("Do you help with Goethe and telc exam preparation?",
            "Yes! Our courses are specially structured to help adult learners clear "
            "official international certifications like Goethe and telc exams with "
            "confidence."),
        Faq("What time zones or schedules do you follow?",
            "All our live classes are scheduled on convenient IST (Indian Standard Time) "
            "timings. You can check our current course schedules, start dates, and "
            "transparent pricing directly on our courses page."),
        Faq("How do I enroll or find out which level is right for me?",
            "Getting started is simple! You can contact us for a free 15-minute placement "
            "chat or drop an enquiry. We will evaluate your current level and match you "
            "with the right course, teacher, and start date."),
    ],
    "courses": [
        Faq("How long does each level take?",
            "Roughly ten to twelve weeks per level at three hours a week, or four weeks "
            "on an intensive. B1 takes longer than A1 and A2 — it is the biggest jump in "
            "the sequence."),
        Faq("Can I join a course that has already started?",
            "Usually within the first two weeks, if there is space and your level fits. "
            "After that you are better off waiting for the next block, and we will hold "
            "a place for you."),
        Faq("What happens if I miss a session?",
            "Evening group sessions are recorded and shared with the class, so you can "
            "catch up. Your teacher will also flag anything important you missed at the "
            "start of the next session."),
        Faq("Do you prepare people for the Goethe and telc exams?",
            "Yes — there is a dedicated eight-week course for B2, and we run A2, B1 and "
            "C1 preparation on request. Markus is a licensed examiner for both boards."),
    ],
    "pricing": [
        Faq("Is there an admission fee?",
            "No. The fee on the course page is the whole fee, including materials, the "
            "placement assessment and your certificate. GST is included."),
        Faq("Can I pay in instalments?",
            "Yes, on any course longer than eight weeks — half at the start and half "
            "midway, with no surcharge. UPI, cards and bank transfer all work."),
        Faq("Do you offer discounts?",
            "Blocks of ten or twenty private hours are cheaper per hour, and full-time "
            "students get a reduced rate on batch courses. Ask us when you enquire."),
        Faq("What does a corporate programme cost?",
            "It depends on team size, level spread and whether it is on site. Tell us "
            "roughly what you need and we will send a written quote within two working "
            "days."),
    ],
    "teachers": [
        Faq("Who will be teaching me?",
            "Classes are taught by Jaishree Mudgal, who teaches every level from A1 to "
            "B2 as well as Goethe and telc preparation."),
        Faq("Will I always have the same teacher?",
            "Yes. The same teacher takes your batch from the first session to the last, "
            "which matters far more than variety at this stage."),
        Faq("How big are the batches?",
            "Capped at eight, and usually running with six, so there is time for "
            "everyone to speak in every session."),
    ],
    "process": [
        Faq("How quickly can I start?",
            "New evening groups open every few weeks, and private lessons can usually "
            "start within a week of your placement chat."),
        Faq("Is the placement chat really free?",
            "Yes, and there is no obligation afterwards. If we think another school "
            "suits you better, we will say so."),
        Faq("What happens in the placement conversation?",
            "Fifteen minutes, half in English and half in German, about ordinary things "
            "— where you live, why you are learning, what you did at the weekend. We "
            "are listening for what you can already do."),
    ],
    "enquiry": [
        Faq("How soon will you reply?",
            "Within one working day, usually the same morning. If it is urgent, call us "
            "and we will pick it up straight away."),
        Faq("Will I be added to a mailing list?",
            "No. We reply to your enquiry and that is it. No newsletter, and no sales "
            "calls out of the blue."),
    ],
}
