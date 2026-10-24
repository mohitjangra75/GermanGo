"""Populate the site with realistic starter content.

Run with ``python manage.py seed_content``. Idempotent: everything is keyed
on a natural field, so a second run updates rather than duplicates. Use
``--fresh`` to clear the seeded content first.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import (
    Faq, HeroWord, Highlight, ProcessStep, SiteStat, Testimonial,
)
from courses.models import Course, CourseModule
from games.models import MapCity
from pricing.models import Plan, PlanFeature
from teachers.models import Teacher


class Command(BaseCommand):
    help = "Seed GermanGo with starter courses, teachers, pricing and copy."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fresh",
            action="store_true",
            help="Delete existing seeded content before inserting.",
        )

    def say(self, message, style=None):
        if self.verbosity:
            self.stdout.write(style(message) if style else message)

    @transaction.atomic
    def handle(self, *args, **options):
        self.verbosity = options.get("verbosity", 1)

        if options["fresh"]:
            self.say("Clearing seeded content…")
            for model in (Course, Teacher, Plan, Testimonial, SiteStat,
                          ProcessStep, Faq, HeroWord, Highlight, MapCity):
                model.objects.all().delete()

        teachers = self.seed_teachers()
        self.seed_courses(teachers)
        self.seed_pricing()
        self.seed_map_cities()
        self.seed_site_copy()

        self.say("")
        self.say(
            f"Seeded: {Course.objects.count()} courses "
            f"({CourseModule.objects.count()} syllabus modules), "
            f"{Teacher.objects.count()} teachers, "
            f"{Plan.objects.count()} plans, "
            f"{MapCity.objects.count()} map cities, "
            f"{Faq.objects.count()} FAQs, "
            f"{Testimonial.objects.count()} testimonials.",
            self.style.SUCCESS,
        )

    # ------------------------------------------------------------------
    # Teachers
    # ------------------------------------------------------------------

    def seed_teachers(self):
        """The one teacher who runs the school.

        A real, named person: the experience and certification here are the
        ones she supplied, and nothing beyond them is invented. The rest of
        the copy describes only what the published catalogue commits to.
        """
        teacher, _ = Teacher.objects.update_or_create(
            name="Jaishree Mudgal",
            defaults={
                "role": "Founder & German teacher",
                "headline": "Teaches every level from A1 to B2, in small live "
                            "online batches on IST timings.",
                "bio": "I teach German to adults across India — complete beginners "
                       "through to B2, plus Goethe and telc exam preparation.\n\n"
                       "Batches stay small, capped at eight, so everybody speaks in "
                       "every session. Classes run live over video on IST timings, "
                       "which means no recordings to fall behind on and no awkward "
                       "3am European slots.\n\n"
                       "Before you book anything we have a short placement "
                       "conversation, free and with no obligation, so you start at "
                       "the right level rather than guessing.",
                "home_city": "India · teaches on IST timings",
                "is_native_speaker": False,
                "years_experience": 5,
                "languages": "German, English, Hindi",
                "levels_taught": "A1, A2, B1, B2",
                "specialisms": "Complete beginners starting from zero\n"
                               "Goethe examination preparation\n"
                               "telc examination preparation\n"
                               "Small-batch live online teaching",
                "qualifications": "C1 certified in German",
                "is_featured": True,
                "is_accepting_students": True,
                "order": 0,
            },
        )
        self.say("  · 1 teacher")
        return {"Jaishree Mudgal": teacher}

    # ------------------------------------------------------------------
    # Courses
    # ------------------------------------------------------------------

    def seed_courses(self, teachers):
        """The published catalogue: four levels plus four exam-prep courses."""
        soon = date.today() + timedelta(days=21)

        levels = [
            {
                "title": "German A1 — Beginner Level",
                "level": "A1",
                "price": Decimal("6000"),
                "subtitle": "Basic vocabulary, everyday conversations and the confidence to use them.",
                "description": "A1 is where German stops being a wall of consonants and "
                               "starts being something you can use. You will greet people, "
                               "introduce yourself, order food, handle numbers and times, "
                               "and talk about your family and your day.\n\n"
                               "No previous German is assumed. Most people arrive knowing "
                               "nothing beyond 'danke'.",
                "audience": "Complete beginners with no German at all\n"
                            "Students planning to study in Germany\n"
                            "Professionals joining a German or MNC team\n"
                            "Anyone who prefers learning in a small batch",
                "outcomes": "Build basic vocabulary for daily life\n"
                            "Hold everyday conversations\n"
                            "Introduce yourself and ask about others\n"
                            "Order food and shop for everyday things\n"
                            "Build the confidence to speak out loud",
                "weeks": 10, "hours": Decimal("3.0"),
                "schedule": "Flexible timings (IST)",
                "teachers": ["Jaishree Mudgal"],
                "featured": True, "badge": "Most popular",
                "modules": [
                    ("Weeks 1–2", "Greetings and introductions",
                     "The first conversations you will actually have.",
                     "Formal and informal greetings\ndu and Sie — which to use when\n"
                     "Introducing yourself and asking back\nThe alphabet and spelling your name"),
                    ("Weeks 3–4", "Numbers, time and dates",
                     "Prices, appointments and phone numbers.",
                     "Numbers to one hundred\nTelling the time\nDays, months and dates\n"
                     "Making an appointment"),
                    ("Weeks 5–6", "Food, drink and shopping",
                     "Cafés, bakeries and the supermarket.",
                     "Ordering politely with 'ich hätte gern'\nAsking for the bill\n"
                     "Food and drink vocabulary\nQuantities and prices"),
                    ("Weeks 7–8", "Family, home and daily life",
                     "Talking about yourself at length.",
                     "Family vocabulary\nPossessives: mein, dein, sein\n"
                     "Rooms and furniture\nDescribing a typical day"),
                    ("Weeks 9–10", "Putting it together",
                     "Consolidation and your first extended conversations.",
                     "The accusative case in practice\nWord order: the verb second\n"
                     "Asking for and giving directions\nA final assessed conversation"),
                ],
            },
            {
                "title": "German A2 — Elementary Level",
                "level": "A2",
                "price": Decimal("6000"),
                "subtitle": "More vocabulary, simple grammar and real-life situations.",
                "description": "At A2 you stop translating in your head quite so often. "
                               "This course covers the past tense, appointments, travel and "
                               "the dative case — the tools you need to get through an "
                               "ordinary day in German.\n\n"
                               "You should be comfortable with the present tense before "
                               "joining. If you are unsure, we place you in a free chat first.",
                "audience": "Anyone who has finished A1 here or elsewhere\n"
                            "People who can introduce themselves but stall after that\n"
                            "Students building towards a B1 requirement",
                "outcomes": "Widen your everyday vocabulary\n"
                            "Use simple grammar accurately\n"
                            "Handle real-life situations on your own\n"
                            "Talk about the past with the Perfekt tense\n"
                            "Write short personal messages and emails",
                "weeks": 10, "hours": Decimal("3.0"),
                "schedule": "Flexible timings (IST)",
                "teachers": ["Jaishree Mudgal"],
                "featured": True, "badge": "",
                "modules": [
                    ("Weeks 1–3", "Talking about the past",
                     "The Perfekt tense, which is how Germans speak about yesterday.",
                     "Perfekt with haben and sein\nPast participles\n"
                     "Telling the story of your weekend\nSequencing: zuerst, dann, danach"),
                    ("Weeks 4–6", "Appointments and services",
                     "Doctors, landlords, offices and the phone.",
                     "Making an appointment by phone\nThe dative case\n"
                     "Modal verbs: können, müssen, dürfen\nPolite requests"),
                    ("Weeks 7–8", "Travel and directions",
                     "Stations, tickets and finding your way.",
                     "Buying tickets and reading announcements\n"
                     "Two-way prepositions\nGiving directions\nBooking accommodation"),
                    ("Weeks 9–10", "Describing and comparing",
                     "Opinions, preferences and longer answers.",
                     "Adjective endings, simply explained\nComparatives\n"
                     "Giving a reason with weil\nA final assessed conversation"),
                ],
            },
            {
                "title": "German B1 — Intermediate Level",
                "level": "B1",
                "price": Decimal("7500"),
                "subtitle": "Complex sentences, expressing your opinion and feeling more confident.",
                "description": "B1 is the threshold level, and the one most people actually "
                               "need — for a university place, a work visa, or simply feeling "
                               "at home in the language.\n\n"
                               "You will learn to give and justify an opinion, use subordinate "
                               "clauses naturally, and deal with most situations that come up. "
                               "Twelve weeks rather than ten, because the jump from A2 is the "
                               "biggest in the sequence.",
                "audience": "Anyone who has completed A2\n"
                            "Applicants who need B1 for a university place or visa\n"
                            "People who understand a lot but cannot yet argue a point",
                "outcomes": "Build and understand complex sentences\n"
                            "Express and justify your opinion\n"
                            "Use weil, dass, wenn and obwohl naturally\n"
                            "Follow the main points of clear standard speech\n"
                            "Feel genuinely more confident speaking",
                "weeks": 12, "hours": Decimal("3.0"),
                "schedule": "Flexible timings (IST)",
                "teachers": ["Jaishree Mudgal"],
                "featured": True, "badge": "Needed for visas",
                "modules": [
                    ("Weeks 1–3", "Opinions and argument",
                     "Saying what you think and why.",
                     "Expressing and justifying an opinion\nAgreeing and disagreeing\n"
                     "Subordinate clauses with weil and dass\nDiscussion every session"),
                    ("Weeks 4–6", "Work and study",
                     "The German of applications and workplaces.",
                     "Describing your job\nWriting a formal email\n"
                     "Relative clauses\nInterview role play"),
                    ("Weeks 7–9", "Politeness and hypotheticals",
                     "Konjunktiv II, and how to sound less blunt.",
                     "Würde, hätte, könnte, wäre\nPolite requests\n"
                     "Talking about plans and conditions\nHandling complaints"),
                    ("Weeks 10–12", "Media and longer texts",
                     "Reading and listening beyond the classroom.",
                     "Reading news for gist\nSummarising what you read\n"
                     "Passive voice, introduced\nA final presentation"),
                ],
            },
            {
                "title": "German B2 — Upper Intermediate Level",
                "level": "B2",
                "price": Decimal("8500"),
                "subtitle": "Advanced grammar, fluent communication, career and study ready.",
                "description": "At B2 you argue a point, follow a debate and read a "
                               "newspaper without a dictionary at your elbow. The grammar "
                               "shifts from survival to precision: passive voice, relative "
                               "clauses and nominalisation.\n\n"
                               "This is the level most German employers and universities "
                               "treat as genuinely work-ready.",
                "audience": "Anyone who has completed B1\n"
                            "Candidates who need B2 for work or a Master's place\n"
                            "Professionals working day to day with German colleagues",
                "outcomes": "Handle advanced grammar with precision\n"
                            "Communicate fluently and without obvious searching\n"
                            "Argue a position and weigh alternatives\n"
                            "Follow extended speech and complex argument\n"
                            "Be ready for a German career or degree",
                "weeks": 12, "hours": Decimal("3.5"),
                "schedule": "Flexible timings (IST)",
                "teachers": ["Jaishree Mudgal"],
                "featured": False, "badge": "",
                "modules": [
                    ("Weeks 1–3", "Precision grammar",
                     "The structures that separate correct German from natural German.",
                     "Passive voice in all tenses\nRelative clauses\n"
                     "Nominalisation\nConnectors and register"),
                    ("Weeks 4–6", "Argument and debate",
                     "Holding a position under pressure.",
                     "Structuring an argument\nConceding a point gracefully\n"
                     "Formal and informal register\nWeekly debates"),
                    ("Weeks 7–9", "Professional German",
                     "Meetings, reports and correspondence.",
                     "Meeting language\nWriting a report\n"
                     "Industry vocabulary\nPresenting to a group"),
                    ("Weeks 10–12", "Media and consolidation",
                     "Authentic material at full speed.",
                     "News, podcasts and long reads\nSummarising and responding\n"
                     "A final assessed presentation"),
                ],
            },
        ]

        exam_levels = [
            ("A1", Decimal("7999"), 6, "Flexible timings (IST)"),
            ("A2", Decimal("7999"), 6, "Flexible timings (IST)"),
            ("B1", Decimal("9599"), 8, "Flexible timings (IST)"),
            ("B2", Decimal("11599"), 8, "Flexible timings (IST)"),
        ]

        order = 0
        for spec in levels:
            course, _ = Course.objects.update_or_create(
                title=spec["title"],
                defaults={
                    "level_code": spec["level"],
                    "subtitle": spec["subtitle"],
                    "description": spec["description"],
                    "who_is_it_for": spec["audience"],
                    "outcomes": spec["outcomes"],
                    "course_format": Course.Format.GROUP,
                    "delivery": Course.Delivery.ONLINE,
                    "duration_weeks": spec["weeks"],
                    "hours_per_week": spec["hours"],
                    "max_class_size": 8,
                    "schedule_note": spec["schedule"],
                    "next_start_date": soon + timedelta(days=order * 7),
                    "price": spec["price"],
                    "currency": "INR",
                    "is_featured": spec["featured"],
                    "badge": spec.get("badge", ""),
                    "order": order,
                },
            )
            course.teachers.set([teachers[n] for n in spec["teachers"] if n in teachers])
            course.modules.all().delete()
            for module_order, (weeks, title, summary, topics) in enumerate(spec["modules"]):
                CourseModule.objects.create(
                    course=course, week_range=weeks, title=title,
                    summary=summary, topics=topics, order=module_order,
                )
            order += 1

        # Goethe and telc preparation, one course per level.
        for code, price, weeks, schedule in exam_levels:
            course, _ = Course.objects.update_or_create(
                title=f"German {code} — Exam Preparation (Goethe + telc)",
                defaults={
                    "level_code": code,
                    "subtitle": f"Get ready for your Goethe and telc {code} examinations.",
                    "description": f"This is not a general {code} course. It assumes you "
                                   f"are already at or near {code} and need the certificate "
                                   "— for a university place, a visa or an employer.\n\n"
                                   "Every session works on exam technique: what the "
                                   "examiners want, where candidates routinely lose marks, "
                                   "and how to manage the clock in each paper. Both the "
                                   "Goethe-Zertifikat and telc formats are covered.",
                    "who_is_it_for": f"Candidates already close to {code}\n"
                                     "Anyone with a booked exam date\n"
                                     "Students who need the certificate for a university place\n"
                                     "Professionals needing proof of level for a visa",
                    "outcomes": "Know the format and marking of all four papers\n"
                                "Manage your time under exam conditions\n"
                                "Produce a structured written answer\n"
                                "Handle the speaking task with confidence\n"
                                "Sit at least two full mock examinations",
                    "course_format": Course.Format.EXAM,
                    "delivery": Course.Delivery.ONLINE,
                    "duration_weeks": weeks,
                    "hours_per_week": Decimal("3.0"),
                    "max_class_size": 6,
                    "schedule_note": schedule,
                    "next_start_date": soon + timedelta(days=order * 7),
                    "price": price,
                    "currency": "INR",
                    "is_featured": False,
                    "order": order,
                },
            )
            course.teachers.set(list(teachers.values()))
            course.modules.all().delete()
            for module_order, (weeks_label, title, summary, topics) in enumerate([
                ("Part 1", "Lesen and Hören",
                 "The receptive papers, and how to read the questions.",
                 "Question types in each part\nSkimming under time pressure\n"
                 "Common distractor patterns"),
                ("Part 2", "Schreiben",
                 "The written paper, where most marks are lost.",
                 "Structuring your answer\nRegister and connectors\n"
                 "Marked practice every week"),
                ("Part 3", "Sprechen",
                 "The speaking task, rehearsed until it is routine.",
                 "Presentation structure and timing\nReacting to a partner\n"
                 "Recovering from a blank"),
                ("Part 4", "Full mock examinations",
                 "Two complete papers under real conditions.",
                 "Timed mock under exam conditions\nIndividual feedback on every paper\n"
                 "A final readiness verdict"),
            ]):
                CourseModule.objects.create(
                    course=course, week_range=weeks_label, title=title,
                    summary=summary, topics=topics, order=module_order,
                )
            order += 1

        self.say(f"  · {len(levels)} level courses + {len(exam_levels)} exam-prep courses")

    # ------------------------------------------------------------------
    # Pricing
    # ------------------------------------------------------------------

    def seed_pricing(self):
        """The bundles: learn more levels, pay less."""
        specs = [
            {
                "name": "A1 + A2 Together",
                "tagline": "Best value for beginners.",
                "description": "The two beginner levels booked together, from your first "
                               "Hallo to handling an ordinary day in German. Saves ₹1,001 "
                               "against booking them separately.",
                "price": Decimal("10999"),
                "note": "Both levels · saves ₹1,001 against separate booking",
                "class_size": "Maximum 8 per batch",
                "hours": "3 hours a week, 20 weeks",
                "badge": "Best for beginners",
                "featured": False,
                "colour": "#B98600",
                "cta": "Enquire about A1 + A2",
                "courses": ["German A1 — Beginner Level", "German A2 — Elementary Level"],
                "features": [
                    ("Both levels, one enrolment", True),
                    ("Same teacher across both", True),
                    ("Course materials included", True),
                    ("Free placement conversation", True),
                    ("Certificate after each level", True),
                    ("Goethe / telc exam coaching", False),
                ],
            },
            {
                "name": "B1 + B2 Together",
                "tagline": "Take your skills to the next level.",
                "description": "The two intermediate levels booked together — the pair "
                               "that takes you from getting by to genuinely work-ready. "
                               "Saves ₹1,001 against booking separately.",
                "price": Decimal("14999"),
                "note": "Both levels · saves ₹1,001 against separate booking",
                "class_size": "Maximum 8 per batch",
                "hours": "3–3.5 hours a week, 24 weeks",
                "badge": "Next level",
                "featured": False,
                "colour": "#2F5D8C",
                "cta": "Enquire about B1 + B2",
                "courses": ["German B1 — Intermediate Level", "German B2 — Upper Intermediate Level"],
                "features": [
                    ("Both levels, one enrolment", True),
                    ("Career and study ready by the end", True),
                    ("Course materials included", True),
                    ("Free placement conversation", True),
                    ("Certificate after each level", True),
                    ("Goethe / telc exam coaching", False),
                ],
            },
            {
                "name": "A1 to B2 — All Levels",
                "tagline": "The complete German learning journey.",
                "description": "Every level from absolute beginner to upper intermediate, "
                               "booked as one journey with one teacher team following you "
                               "the whole way. Saves ₹3,401 against booking level by level.",
                "price": Decimal("24599"),
                "note": "All four levels · saves ₹3,401 against separate booking",
                "class_size": "Maximum 8 per batch",
                "hours": "3–3.5 hours a week, 44 weeks",
                "badge": "Complete journey",
                "featured": True,
                "colour": "#C0261A",
                "cta": "Enquire about the full journey",
                "courses": [
                    "German A1 — Beginner Level",
                    "German A2 — Elementary Level",
                    "German B1 — Intermediate Level",
                    "German B2 — Upper Intermediate Level",
                ],
                "features": [
                    ("All four levels, one enrolment", True),
                    ("A single plan from beginner to B2", True),
                    ("Course materials included", True),
                    ("Free placement conversation", True),
                    ("Certificate after each level", True),
                    ("Priority place in the next batch", True),
                ],
            },
        ]

        for order, spec in enumerate(specs):
            plan, _ = Plan.objects.update_or_create(
                name=spec["name"],
                defaults={
                    "tagline": spec["tagline"],
                    "description": spec["description"],
                    "price": spec["price"],
                    "currency": "INR",
                    "period": Plan.Period.COURSE,
                    "price_note": spec["note"],
                    "class_size": spec["class_size"],
                    "hours_included": spec["hours"],
                    "badge": spec["badge"],
                    "is_featured": spec["featured"],
                    "accent_color": spec["colour"],
                    "cta_label": spec["cta"],
                    "order": order,
                },
            )
            plan.features.all().delete()
            for feature_order, (text, included) in enumerate(spec["features"]):
                PlanFeature.objects.create(
                    plan=plan, text=text, is_included=included, order=feature_order
                )
            plan.courses.set(Course.objects.filter(title__in=spec["courses"]))

        self.say(f"  · {len(specs)} course bundles")

    # ------------------------------------------------------------------
    # Map quiz cities
    # ------------------------------------------------------------------

    def seed_map_cities(self):
        # x runs -1 (west) to 1 (east); z runs -1 (north) to 1 (south).
        specs = [
            ("Berlin", "Berlin", 0.42, -0.42, 1, 3850809, "#C0261A",
             "In the north-east, closer to Poland than to the Rhine.",
             "Berlin has more bridges than Venice — around 1,700 of them.",
             "Ich hätte gern einen Kaffee.", "I would like a coffee."),
            ("Munich", "Bayern", 0.18, 0.62, 1, 1512491, "#2A6F52",
             "Deep in the south, with the Alps an hour away.",
             "The Oktoberfest mostly happens in September.",
             "Grüß Gott!", "Hello! (southern greeting)"),
            ("Hamburg", "Hamburg", 0.04, -0.66, 1, 1892122, "#2F5D8C",
             "The great northern port, on the Elbe.",
             "Hamburg's Speicherstadt is the largest warehouse district in the world.",
             "Moin!", "Hello! (northern, any time of day)"),
            ("Cologne", "Nordrhein-Westfalen", -0.54, 0.06, 1, 1073096, "#B98600",
             "West, on the Rhine, with the twin-spired cathedral.",
             "Cologne Cathedral took 632 years to finish.",
             "Kölle Alaaf!", "The Cologne carnival cry"),
            ("Frankfurt", "Hessen", -0.30, 0.20, 1, 773068, "#E63329",
             "Centre-west: the skyline of banks and the busiest airport.",
             "Frankfurt Airport connects to more countries than any other.",
             "Sprechen Sie Englisch?", "Do you speak English?"),
            ("Stuttgart", "Baden-Württemberg", -0.22, 0.52, 2, 630305, "#7A4B9C",
             "South-west, in a valley surrounded by vineyards.",
             "Both Mercedes-Benz and Porsche were founded here.",
             "Wo ist der Bahnhof?", "Where is the train station?"),
            ("Dresden", "Sachsen", 0.52, 0.02, 2, 556227, "#2A6F52",
             "East, on the Elbe, near the Czech border.",
             "Dresden's Frauenkirche was rebuilt from its own rubble.",
             "Wie viel kostet das?", "How much does that cost?"),
            ("Leipzig", "Sachsen", 0.36, -0.06, 2, 601866, "#CA6702",
             "East-central, an hour or so north-west of Dresden.",
             "Bach worked at the Thomaskirche here for 27 years.",
             "Ich verstehe nicht.", "I do not understand."),
            ("Düsseldorf", "Nordrhein-Westfalen", -0.58, -0.04, 2, 619294, "#2F5D8C",
             "West, on the Rhine, just north of Cologne.",
             "It has the largest Japanese community in Germany.",
             "Können Sie mir helfen?", "Can you help me?"),
            ("Bremen", "Bremen", -0.14, -0.56, 3, 566573, "#B98600",
             "North-west, inland from the coast on the Weser.",
             "The Bremen Town Musicians never actually reach Bremen in the tale.",
             "Entschuldigung!", "Excuse me!"),
            ("Nuremberg", "Bayern", 0.16, 0.36, 3, 518370, "#C0261A",
             "Northern Bavaria, between Frankfurt and Munich.",
             "Its Christkindlesmarkt is the most famous Christmas market in Germany.",
             "Frohe Weihnachten!", "Merry Christmas!"),
            ("Hanover", "Niedersachsen", -0.08, -0.32, 3, 535932, "#7A4B9C",
             "North-central, on the route between Berlin and the Ruhr.",
             "The clearest standard German is often said to be spoken here.",
             "Sprechen Sie langsamer, bitte.", "Please speak more slowly."),
        ]

        for order, row in enumerate(specs):
            (name, state, x, z, difficulty, population, colour,
             hint, fact, phrase, phrase_en) = row
            MapCity.objects.update_or_create(
                name=name,
                defaults={
                    "state": state,
                    "map_x": x,
                    "map_z": z,
                    "difficulty": difficulty,
                    "population": population,
                    "accent_color": colour,
                    "hint": hint,
                    "fun_fact": fact,
                    "german_phrase": phrase,
                    "german_phrase_en": phrase_en,
                    "order": order,
                },
            )

        self.say(f"  · {len(specs)} map cities")

    # ------------------------------------------------------------------
    # Site copy
    # ------------------------------------------------------------------

    def seed_site_copy(self):
        steps = [
            ("01", "Tell us where you are", "compass",
             "Send a short message — your name, roughly your level and what you want "
             "German for. You do not need to know your CEFR level; most people don't.",
             "There is no form to fill in beyond four fields, and no obligation. If "
             "you would rather phone, the number is at the top of every page."),
            ("02", "A free placement chat", "chat",
             "We book a fifteen-minute conversation, half in English and half in "
             "German. It tells us far more than a written test would.",
             "It is genuinely a conversation, not an exam. We are listening for what "
             "you can already do, not counting your mistakes. At the end we tell you "
             "which level you belong in — even if that means a course we are not "
             "currently running."),
            ("03", "We match a course and a teacher", "users",
             "You get a specific recommendation: this course, this teacher, this start "
             "date, this price. If nothing fits, we say so.",
             "Teachers are matched on more than level. Someone preparing for a B2 exam "
             "in six weeks needs a different person from someone learning German for "
             "the pleasure of it, and we will explain why we picked who we picked."),
            ("04", "Start, and keep going", "sparkle",
             "Lessons begin. You are reviewed every few weeks, and moved up when you "
             "are ready rather than when the calendar says so.",
             "If a course turns out to be wrong for you, tell us within the first two "
             "sessions and we will move you to a batch that fits better. Fees are "
             "non-refundable, which is why the placement chat comes first."),
        ]
        for order, (number, title, icon, body, detail) in enumerate(steps):
            ProcessStep.objects.update_or_create(
                number=number,
                defaults={
                    "title": title, "icon": icon, "body": body,
                    "detail": detail, "order": order,
                },
            )

        # Structural facts only. Anything like "2,400 students taught" or a
        # pass-rate percentage would be an unverifiable claim on a live site,
        # so add those in the admin once there are real figures behind them.
        stats = [
            ("Levels taught", "A1–B2", "Plus Goethe & telc preparation", 0),
            ("Maximum batch size", "8", "Usually runs with six", 1),
            ("Courses from", "₹6,000", "For a full 10-week level", 2),
            ("Reply time", "< 1 day", "Usually the same morning", 3),
        ]
        for label, value, caption, order in stats:
            SiteStat.objects.update_or_create(
                label=label, defaults={"value": value, "caption": caption, "order": order}
            )

        testimonials = [
            ("Priya Raghavan", "Software engineer, Bengaluru → Berlin", "Reached B1 in 9 months",
             "I had tried two apps and got nowhere. What worked here was being made to "
             "speak in the very first session, badly, in front of other people who were "
             "also speaking badly. Six weeks later I renewed my own residence permit in "
             "German.", 5, 0),
            ("Arjun Menon", "Masters applicant, Kochi", "Passed Goethe B2",
             "Markus knew the exam better than I knew my own subject. He told me exactly "
             "where I was losing marks on the writing paper — something nobody had "
             "mentioned in two years of general classes. Passed first time.", 5, 1),
            ("Sneha Patil", "Nurse, Pune → Düsseldorf", "A1 to B1 in a year",
             "The intensive month was hard and I nearly dropped out in week two. Lena "
             "noticed and changed how she was teaching me rather than letting me quit. "
             "I now work entirely in German.", 5, 2),
        ]
        # Seeded unpublished on purpose. These are written examples, not real
        # students — publishing invented quotes under invented names would be
        # misleading. Replace the text with genuine feedback, then tick
        # "is published" in the admin.
        for name, role, level, quote, rating, order in testimonials:
            Testimonial.objects.update_or_create(
                name=name,
                defaults={
                    "role": role, "level_reached": level, "quote": quote,
                    "rating": rating, "order": order, "is_published": False,
                },
            )

        faqs = [
            (Faq.Page.HOME, "Do I need to know my level before enquiring?",
             "No. Most people have no idea, and a self-assessment is usually wrong in "
             "one direction or the other. We run a free fifteen-minute placement chat "
             "and tell you where you belong."),
            (Faq.Page.HOME, "Are classes live or recorded?",
             "All batches run live online over video, on IST timings, so you can join "
             "from anywhere in India. They are live classes with a real teacher, not "
             "recordings."),
            (Faq.Page.HOME, "How big are the groups?",
             "Evening batches are capped at eight and usually run with six. Intensives "
             "are capped at six. We do not exceed those numbers to fit one more person in."),
            (Faq.Page.HOME, "What if the course turns out to be wrong for me?",
             "Tell us within the first two sessions and we will move you to a batch "
             "that suits you better. Fees are non-refundable, so we use the free "
             "placement chat to get your level right before you enrol."),

            (Faq.Page.COURSES, "How long does each level take?",
             "Roughly ten to twelve weeks per level at three hours a week, or four "
             "weeks on an intensive. B1 takes longer than A1 and A2 — it is the biggest "
             "jump in the sequence."),
            (Faq.Page.COURSES, "Can I join a course that has already started?",
             "Usually within the first two weeks, if there is space and your level "
             "fits. After that you are better off waiting for the next block, and we "
             "will hold a place for you."),
            (Faq.Page.COURSES, "What happens if I miss a session?",
             "Evening group sessions are recorded and shared with the class, so you "
             "can catch up. Your teacher will also flag anything important you missed "
             "at the start of the next session."),
            (Faq.Page.COURSES, "Do you prepare people for the Goethe and telc exams?",
             "Yes — there is a dedicated eight-week course for B2, and we run A2, B1 "
             "and C1 preparation on request. Markus is a licensed examiner for both boards."),

            (Faq.Page.PRICING, "Is there an admission fee?",
             "No. The fee on the course page is the whole fee, including materials, the "
             "placement assessment and your certificate. GST is included."),
            (Faq.Page.PRICING, "Can I pay in instalments?",
             "Yes, on any course longer than eight weeks — half at the start and half "
             "midway, with no surcharge. UPI, cards and bank transfer all work."),
            (Faq.Page.PRICING, "Do you offer discounts?",
             "Blocks of ten or twenty private hours are cheaper per hour, and full-time "
             "students get a reduced rate on batch courses. Ask us when you enquire."),
            (Faq.Page.PRICING, "What does a corporate programme cost?",
             "It depends on team size, level spread and whether it is on site. Tell us "
             "roughly what you need and we will send a written quote within two working days."),

            (Faq.Page.TEACHERS, "Who will be teaching me?",
             "Classes are taught by Jaishree Mudgal, who teaches every level from A1 "
             "to B2 as well as Goethe and telc preparation."),
            (Faq.Page.TEACHERS, "Will I always have the same teacher?",
             "Yes. The same teacher takes your batch from the first session to the "
             "last, which matters far more than variety at this stage."),
            (Faq.Page.TEACHERS, "How big are the batches?",
             "Capped at eight, and usually running with six, so there is time for "
             "everyone to speak in every session."),

            (Faq.Page.PROCESS, "How quickly can I start?",
             "New evening groups open every few weeks, and private lessons can usually "
             "start within a week of your placement chat."),
            (Faq.Page.PROCESS, "Is the placement chat really free?",
             "Yes, and there is no obligation afterwards. If we think another school "
             "suits you better, we will say so."),
            (Faq.Page.PROCESS, "What happens in the placement conversation?",
             "Fifteen minutes, half in English and half in German, about ordinary "
             "things — where you live, why you are learning, what you did at the "
             "weekend. We are listening for what you can already do."),

            (Faq.Page.ENQUIRY, "How soon will you reply?",
             "Within one working day, usually the same morning. If it is urgent, call "
             "us and we will pick it up straight away."),
            (Faq.Page.ENQUIRY, "Will I be added to a mailing list?",
             "No. We reply to your enquiry and that is it. No newsletter, and no sales "
             "calls out of the blue."),
        ]
        for order, (page, question, answer) in enumerate(faqs):
            Faq.objects.update_or_create(
                question=question,
                defaults={"page": page, "answer": answer, "order": order},
            )

        # The reassurance band under the hero.
        trust = [
            ("Flexible Learning", "laptop", "Live online batches, flexible timings", 0),
            ("Expert Guidance", "users", "C1-certified teacher, 5 years' experience", 1),
            ("Structured Curriculum", "layers", "A clear path from A1 to B2", 2),
            ("Lifetime Access", "shield", "Keep your materials and recordings", 3),
        ]
        for title, icon, description, order in trust:
            Highlight.objects.update_or_create(
                title=title,
                section=Highlight.Section.TRUST,
                defaults={"icon": icon, "description": description, "order": order},
            )

        # "Opportunities after learning German" — the reason people enrol.
        opportunities = [
            ("Study in Germany", "graduation",
             "Get admission to top universities with German language skills.",
             "#B98600", 0),
            ("Better Job Opportunities", "briefcase",
             "Work in MNCs, German companies or global firms.",
             "#2A6F52", 1),
            ("Travel the World", "plane",
             "Explore Germany and other European countries easily.",
             "#C0261A", 2),
            ("Connect with People", "users",
             "Make new friends and experience different cultures.",
             "#2F5D8C", 3),
            ("A Brighter Future", "trending",
             "Build a global career and open doors to more opportunities.",
             "#7A4B9C", 4),
        ]
        for title, icon, description, colour, order in opportunities:
            Highlight.objects.update_or_create(
                title=title,
                section=Highlight.Section.OPPORTUNITY,
                defaults={
                    "icon": icon, "description": description,
                    "accent_color": colour, "order": order,
                },
            )

        hero_words = [
            ("", "Hallo", "Hello", "Hallo, ich heiße Anna.", "Hello, my name is Anna."),
            ("", "Danke", "Thank you", "Danke für Ihre Hilfe!", "Thank you for your help!"),
            ("", "Guten Morgen", "Good morning", "Guten Morgen, Herr Weber.", "Good morning, Mr Weber."),
            ("der", "Bahnhof", "train station", "Wo ist der Bahnhof?", "Where is the train station?"),
            ("der", "Freund", "friend", "Er ist mein bester Freund.", "He is my best friend."),
            ("die", "Familie", "family", "Meine Familie wohnt in Köln.", "My family lives in Cologne."),
            ("das", "Haus", "house", "Das Haus ist groß.", "The house is big."),
            ("die", "Arbeit", "work", "Ich gehe um acht zur Arbeit.", "I go to work at eight."),
        ]
        for order, (article, word, translation, de, en) in enumerate(hero_words):
            HeroWord.objects.update_or_create(
                word=word,
                defaults={
                    "article": article, "translation": translation,
                    "example_de": de, "example_en": en, "order": order,
                },
            )

        self.say(
            f"  · {len(steps)} process steps, {len(stats)} stats, "
            f"{len(testimonials)} testimonials, {len(faqs)} FAQs, "
            f"{len(trust)} trust points, {len(opportunities)} opportunities, "
            f"{len(hero_words)} hero words"
        )
