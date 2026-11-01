"""Load the course catalogue that used to live in courses/content.py.

Courses are edited in the admin from here on; this only seeds a fresh
database so the site is never empty.
"""

from django.db import migrations

# Level courses, taken from the school's own course posters.
LEVEL_COURSES = [{'slug': 'german-a1-beginner-level',
  'title': 'German A1 — Beginner Level',
  'level_code': 'A1',
  'price': 6000,
  'subtitle': 'Basic vocabulary, everyday conversations and the confidence to use '
              'them.',
  'description': 'A1 is where German stops being a wall of consonants and starts being '
                 'something you can use. You will greet people, introduce yourself, '
                 'order food, handle numbers and times, and talk about your family and '
                 'your day.\n'
                 '\n'
                 'No previous German is assumed. Most people arrive knowing nothing '
                 "beyond 'danke'.",
  'audience': 'Complete beginners with no German at all\n'
              'Students planning to study in Germany\n'
              'Professionals joining a German or MNC team\n'
              'Anyone who prefers learning in a small batch',
  'outcomes': 'Build basic vocabulary for daily life\n'
              'Hold everyday conversations\n'
              'Introduce yourself and ask about others\n'
              'Order food and shop for everyday things\n'
              'Build the confidence to speak out loud',
  'duration_weeks': 10,
  'hours_per_week': '3.0',
  'schedule_note': 'Flexible timings (IST)',
  'teacher_slugs': ['jaishree-mudgal'],
  'badge': 'Most popular',
  'is_featured': True,
  'modules': [{'week_range': 'Weeks 1–2',
               'title': 'Greetings and introductions',
               'summary': 'The first conversations you will actually have.',
               'topics': 'Formal and informal greetings\n'
                         'du and Sie — which to use when\n'
                         'Introducing yourself and asking back\n'
                         'The alphabet and spelling your name'},
              {'week_range': 'Weeks 3–4',
               'title': 'Numbers, time and dates',
               'summary': 'Prices, appointments and phone numbers.',
               'topics': 'Numbers to one hundred\n'
                         'Telling the time\n'
                         'Days, months and dates\n'
                         'Making an appointment'},
              {'week_range': 'Weeks 5–6',
               'title': 'Food, drink and shopping',
               'summary': 'Cafés, bakeries and the supermarket.',
               'topics': "Ordering politely with 'ich hätte gern'\n"
                         'Asking for the bill\n'
                         'Food and drink vocabulary\n'
                         'Quantities and prices'},
              {'week_range': 'Weeks 7–8',
               'title': 'Family, home and daily life',
               'summary': 'Talking about yourself at length.',
               'topics': 'Family vocabulary\n'
                         'Possessives: mein, dein, sein\n'
                         'Rooms and furniture\n'
                         'Describing a typical day'},
              {'week_range': 'Weeks 9–10',
               'title': 'Putting it together',
               'summary': 'Consolidation and your first extended conversations.',
               'topics': 'The accusative case in practice\n'
                         'Word order: the verb second\n'
                         'Asking for and giving directions\n'
                         'A final assessed conversation'}]},
 {'slug': 'german-a2-elementary-level',
  'title': 'German A2 — Elementary Level',
  'level_code': 'A2',
  'price': 6000,
  'subtitle': 'More vocabulary, simple grammar and real-life situations.',
  'description': 'At A2 you stop translating in your head quite so often. This course '
                 'covers the past tense, appointments, travel and the dative case — '
                 'the tools you need to get through an ordinary day in German.\n'
                 '\n'
                 'You should be comfortable with the present tense before joining. If '
                 'you are unsure, we place you in a free chat first.',
  'audience': 'Anyone who has finished A1 here or elsewhere\n'
              'People who can introduce themselves but stall after that\n'
              'Students building towards a B1 requirement',
  'outcomes': 'Widen your everyday vocabulary\n'
              'Use simple grammar accurately\n'
              'Handle real-life situations on your own\n'
              'Talk about the past with the Perfekt tense\n'
              'Write short personal messages and emails',
  'duration_weeks': 10,
  'hours_per_week': '3.0',
  'schedule_note': 'Flexible timings (IST)',
  'teacher_slugs': ['jaishree-mudgal'],
  'badge': '',
  'is_featured': True,
  'modules': [{'week_range': 'Weeks 1–3',
               'title': 'Talking about the past',
               'summary': 'The Perfekt tense, which is how Germans speak about '
                          'yesterday.',
               'topics': 'Perfekt with haben and sein\n'
                         'Past participles\n'
                         'Telling the story of your weekend\n'
                         'Sequencing: zuerst, dann, danach'},
              {'week_range': 'Weeks 4–6',
               'title': 'Appointments and services',
               'summary': 'Doctors, landlords, offices and the phone.',
               'topics': 'Making an appointment by phone\n'
                         'The dative case\n'
                         'Modal verbs: können, müssen, dürfen\n'
                         'Polite requests'},
              {'week_range': 'Weeks 7–8',
               'title': 'Travel and directions',
               'summary': 'Stations, tickets and finding your way.',
               'topics': 'Buying tickets and reading announcements\n'
                         'Two-way prepositions\n'
                         'Giving directions\n'
                         'Booking accommodation'},
              {'week_range': 'Weeks 9–10',
               'title': 'Describing and comparing',
               'summary': 'Opinions, preferences and longer answers.',
               'topics': 'Adjective endings, simply explained\n'
                         'Comparatives\n'
                         'Giving a reason with weil\n'
                         'A final assessed conversation'}]},
 {'slug': 'german-b1-intermediate-level',
  'title': 'German B1 — Intermediate Level',
  'level_code': 'B1',
  'price': 7500,
  'subtitle': 'Complex sentences, expressing your opinion and feeling more confident.',
  'description': 'B1 is the threshold level, and the one most people actually need — '
                 'for a university place, a work visa, or simply feeling at home in '
                 'the language.\n'
                 '\n'
                 'You will learn to give and justify an opinion, use subordinate '
                 'clauses naturally, and deal with most situations that come up. '
                 'Twelve weeks rather than ten, because the jump from A2 is the '
                 'biggest in the sequence.',
  'audience': 'Anyone who has completed A2\n'
              'Applicants who need B1 for a university place or visa\n'
              'People who understand a lot but cannot yet argue a point',
  'outcomes': 'Build and understand complex sentences\n'
              'Express and justify your opinion\n'
              'Use weil, dass, wenn and obwohl naturally\n'
              'Follow the main points of clear standard speech\n'
              'Feel genuinely more confident speaking',
  'duration_weeks': 12,
  'hours_per_week': '3.0',
  'schedule_note': 'Flexible timings (IST)',
  'teacher_slugs': ['jaishree-mudgal'],
  'badge': 'Needed for visas',
  'is_featured': True,
  'modules': [{'week_range': 'Weeks 1–3',
               'title': 'Opinions and argument',
               'summary': 'Saying what you think and why.',
               'topics': 'Expressing and justifying an opinion\n'
                         'Agreeing and disagreeing\n'
                         'Subordinate clauses with weil and dass\n'
                         'Discussion every session'},
              {'week_range': 'Weeks 4–6',
               'title': 'Work and study',
               'summary': 'The German of applications and workplaces.',
               'topics': 'Describing your job\n'
                         'Writing a formal email\n'
                         'Relative clauses\n'
                         'Interview role play'},
              {'week_range': 'Weeks 7–9',
               'title': 'Politeness and hypotheticals',
               'summary': 'Konjunktiv II, and how to sound less blunt.',
               'topics': 'Würde, hätte, könnte, wäre\n'
                         'Polite requests\n'
                         'Talking about plans and conditions\n'
                         'Handling complaints'},
              {'week_range': 'Weeks 10–12',
               'title': 'Media and longer texts',
               'summary': 'Reading and listening beyond the classroom.',
               'topics': 'Reading news for gist\n'
                         'Summarising what you read\n'
                         'Passive voice, introduced\n'
                         'A final presentation'}]},
 {'slug': 'german-b2-upper-intermediate-level',
  'title': 'German B2 — Upper Intermediate Level',
  'level_code': 'B2',
  'price': 8500,
  'subtitle': 'Advanced grammar, fluent communication, career and study ready.',
  'description': 'At B2 you argue a point, follow a debate and read a newspaper '
                 'without a dictionary at your elbow. The grammar shifts from survival '
                 'to precision: passive voice, relative clauses and nominalisation.\n'
                 '\n'
                 'This is the level most German employers and universities treat as '
                 'genuinely work-ready.',
  'audience': 'Anyone who has completed B1\n'
              "Candidates who need B2 for work or a Master's place\n"
              'Professionals working day to day with German colleagues',
  'outcomes': 'Handle advanced grammar with precision\n'
              'Communicate fluently and without obvious searching\n'
              'Argue a position and weigh alternatives\n'
              'Follow extended speech and complex argument\n'
              'Be ready for a German career or degree',
  'duration_weeks': 12,
  'hours_per_week': '3.5',
  'schedule_note': 'Flexible timings (IST)',
  'teacher_slugs': ['jaishree-mudgal'],
  'badge': '',
  'is_featured': False,
  'modules': [{'week_range': 'Weeks 1–3',
               'title': 'Precision grammar',
               'summary': 'The structures that separate correct German from natural '
                          'German.',
               'topics': 'Passive voice in all tenses\n'
                         'Relative clauses\n'
                         'Nominalisation\n'
                         'Connectors and register'},
              {'week_range': 'Weeks 4–6',
               'title': 'Argument and debate',
               'summary': 'Holding a position under pressure.',
               'topics': 'Structuring an argument\n'
                         'Conceding a point gracefully\n'
                         'Formal and informal register\n'
                         'Weekly debates'},
              {'week_range': 'Weeks 7–9',
               'title': 'Professional German',
               'summary': 'Meetings, reports and correspondence.',
               'topics': 'Meeting language\n'
                         'Writing a report\n'
                         'Industry vocabulary\n'
                         'Presenting to a group'},
              {'week_range': 'Weeks 10–12',
               'title': 'Media and consolidation',
               'summary': 'Authentic material at full speed.',
               'topics': 'News, podcasts and long reads\n'
                         'Summarising and responding\n'
                         'A final assessed presentation'}]}]

# Goethe and telc preparation, one course per level, sharing one syllabus.
EXAM_MODULES = [{'week_range': 'Part 1',
  'title': 'Lesen and Hören',
  'summary': 'The receptive papers, and how to read the questions.',
  'topics': 'Question types in each part\n'
            'Skimming under time pressure\n'
            'Common distractor patterns'},
 {'week_range': 'Part 2',
  'title': 'Schreiben',
  'summary': 'The written paper, where most marks are lost.',
  'topics': 'Structuring your answer\n'
            'Register and connectors\n'
            'Marked practice every week'},
 {'week_range': 'Part 3',
  'title': 'Sprechen',
  'summary': 'The speaking task, rehearsed until it is routine.',
  'topics': 'Presentation structure and timing\n'
            'Reacting to a partner\n'
            'Recovering from a blank'},
 {'week_range': 'Part 4',
  'title': 'Full mock examinations',
  'summary': 'Two complete papers under real conditions.',
  'topics': 'Timed mock under exam conditions\n'
            'Individual feedback on every paper\n'
            'A final readiness verdict'}]


def exam_course(code, price, weeks):
    return {
        "slug": f"german-{code.lower()}-exam-preparation-goethe-telc",
        "title": f"German {code} — Exam Preparation (Goethe + telc)",
        "level_code": code,
        "price": price,
        "subtitle": f"Get ready for your Goethe and telc {code} examinations.",
        "description": f"This is not a general {code} course. It assumes you are already "
        f"at or near {code} and need the certificate — for a university place, a visa "
        "or an employer.\n\n"
        "Every session works on exam technique: what the examiners want, where "
        "candidates routinely lose marks, and how to manage the clock in each paper. "
        "Both the Goethe-Zertifikat and telc formats are covered.",
        "audience": f"Candidates already close to {code}\n"
        "Anyone with a booked exam date\n"
        "Students who need the certificate for a university place\n"
        "Professionals needing proof of level for a visa",
        "outcomes": "Know the format and marking of all four papers\n"
        "Manage your time under exam conditions\n"
        "Produce a structured written answer\n"
        "Handle the speaking task with confidence\n"
        "Sit at least two full mock examinations",
        "course_format": "exam",
        "duration_weeks": weeks,
        "max_class_size": 6,
        "schedule_note": "Flexible timings (IST)",
        "teacher_slugs": ["jaishree-mudgal"],
        "modules": EXAM_MODULES,
    }


COURSES = LEVEL_COURSES + [
    exam_course("A1", 7999, weeks=6),
    exam_course("A2", 7999, weeks=6),
    exam_course("B1", 9599, weeks=8),
    exam_course("B2", 11599, weeks=8),
]


def load_courses(apps, schema_editor):
    Course = apps.get_model("courses", "Course")
    CourseModule = apps.get_model("courses", "CourseModule")
    for order, spec in enumerate(COURSES):
        spec = dict(spec)
        modules = spec.pop("modules")
        course = Course.objects.create(order=order, **spec)
        CourseModule.objects.bulk_create(
            CourseModule(course=course, order=index, **module)
            for index, module in enumerate(modules)
        )


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0005_course_in_admin"),
    ]

    operations = [
        migrations.RunPython(load_courses, migrations.RunPython.noop),
    ]
