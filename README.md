# GermanGo

A marketing website for a German language school in India, built entirely on
Django. It exists to show courses, fees, teachers and how the school works —
and to turn visitors into enquiries.

There is no student login and no learning software. Every page ends in the
same place: a short form that lands in the admin. Fees are in rupees, and a
free map quiz gives visitors a reason to stay long enough to enquire.

```
Django Templates + HTML/CSS + Vanilla JS + HTMX + GSAP + Three.js
```

---

## Quick start

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_content     # realistic courses, teachers, prices, copy
python manage.py createsuperuser
python manage.py runserver
```

- Site — http://127.0.0.1:8000/
- Admin — http://127.0.0.1:8000/admin/

SQLite is used by default and the database file is created for you. There is
no `.env` and nothing to configure to get started.

---

## Pages

| URL | What it does |
|-----|--------------|
| `/` | Hero, courses, process, teachers, pricing, proof, FAQ, enquiry |
| `/courses/` | Filterable list of every course |
| `/courses/<slug>/` | One course: price, schedule, syllabus, teachers, enquiry |
| `/teachers/` | Filterable teacher directory |
| `/teachers/<slug>/` | One teacher: bio, specialisms, qualifications, enquiry |
| `/pricing/` | Plans side by side, plus a full course price table |
| `/how-it-works/` | The four steps from enquiry to first lesson |
| `/game/germany-map/` | The 3D Germany map quiz |
| `/enquiry/` | The enquiry form on its own page |
| `/admin/` | Where staff manage all of the above |

---

## Project layout

```
GermanGo/
├── manage.py
├── config/            settings (one file, no env), urls, wsgi, asgi
│
├── core/              shared mixins, homepage, process page, SEO, sitemaps
│   ├── models.py        Testimonial, SiteStat, ProcessStep, Faq, HeroWord
│   ├── seo.py           SeoData + schema.org builders
│   ├── templatetags/    germango.py, registered as template builtins
│   └── management/commands/seed_content.py
│
├── courses/           Course + CourseModule (the syllabus outline)
├── teachers/          Teacher profiles
├── pricing/           Plan + PlanFeature
├── games/             MapCity + GamePlay — the Germany map quiz
├── leads/             Enquiry, the form, spam handling, the admin inbox
│
├── templates/
│   ├── base.html
│   ├── components/    logo, navbar, footer, cards, enquiry block, FAQ, icons
│   ├── home/ courses/ teachers/ pricing/ games/ leads/
│   └── */partials/    HTMX fragments
│
└── static/
    ├── css/           tokens · components · pages
    ├── js/            main, forms, navigation, animations, utils,
    │                  three-hero, germany-map, map-quiz
    ├── vendor/        htmx, gsap, ScrollTrigger, three (all self-hosted)
    └── images/
```

Nothing on the site is hard-coded in a template. Courses, teachers, plans,
process steps, testimonials, statistics and FAQs all come from the database.

---

## Layout and motion

**One 80% column.** The navbar, every section and the footer share it via
`.wrap`, which is `min(80%, 1440px)` from 900px up and falls back to fixed
gutters on mobile. `.bleed` opts a section out of it.

The **hero is the one full-bleed section**. Its copy still starts on the same
10% line as everything else; only the 3D scene runs out to the right edge,
which is what makes the full width worth having.

> If you add a component that also carries `.wrap`, do not give it a width.
> A `width: 100%` declared later in the cascade silently overrides the shared
> column — that bug is why the navbar once sat flush to the viewport edge
> while every section below it was correctly inset.

**Spacing is deliberately tight.** `.section` padding is
`clamp(32px, 4.5vw, 64px)` — roughly half what it was — because a short
marketing page with generous section padding reads as having run out of
things to say. Section headings, the hero, page headers and the enquiry band
were all pulled in to match.

**The opening curtain**, on the homepage only: red and gold fabric panels
draw apart to reveal the page, under a black pelmet trimmed in the flag's
colours. It is an arrival moment, so no other page carries the markup at
all — playing it on every internal click would be an interruption rather
than a flourish.

The fabric is two repeating gradients at different periods — one gradient
alone reads as corrugation, two make cloth — plus vertical shading where it
hangs and pools. Each panel is *scaled* toward its outer edge rather than
merely slid, so the folds compress as it opens, which is how a real curtain
gathers.

Only `transform` and `opacity` are animated, so it runs on the compositor
and cannot cause jank. The whole sequence is about 1.6 seconds.

It cannot trap anyone. `animation-fill-mode: both` leaves the panels
gathered away and the overlay is hidden by CSS at 1700ms, so it finishes
open even if JavaScript never runs; the click blocker releases itself at
700ms; and where JavaScript is available it deletes the element outright
rather than leaving a fixed full-viewport overlay to a timing assumption.
Skipped entirely under reduced motion.

`CURTAIN_MODE` in settings controls how often it plays:

| Value | Behaviour |
|-------|-----------|
| `"always"` *(current)* | Every page load |
| `"session"` | Once per browser tab, then out of the way |
| `"off"` | Never |

> `?curtain=1` forces it regardless of mode. In `session` mode the flag is
> kept in `sessionStorage`, so a reload will *not* replay it — which looks
> exactly like the curtain being broken.

**Nothing on the site explains browser capabilities to visitors.** When a 3D
scene cannot run, its container quietly shows the same choices in plain form
— a word cloud, or the city buttons — with no mention of WebGL, and any
chrome that refers to the scene ("click a marker") is hidden with it.

---

## Brand and currency

The logo is drawn as inline SVG in `templates/components/logo_mark.html`, so
it stays crisp at any size, inherits the surrounding colour and flips to a
light version on the dark footer. Pass `with_tagline=True` to include the
brand line, *Learn German • Grow Your World* (the footer does).

Its geometry is traced from the brand artwork, anchored on the G's centre
and radius so every point is in proportion. The plane's red upper wing and
gold lower wing double as the letter's bar, which is why no separate
crossbar is drawn. It stays legible down to 20px — checked at 280, 96, 52,
34 and 20. `static/images/logo-mark.svg`,
`favicon.svg` and `og-default.svg` carry the same artwork for places that
need a file.

Its three colours drive the palette, set in `static/css/tokens.css`:

| Token | Value | Used for |
|-------|-------|----------|
| `--brand-ink` | `#15161A` | The mark, headings, body text |
| `--brand-red` | `#E63329` | The mark only |
| `--brand-gold` | `#F5B821` | The mark only |
| `--red` | `#C0261A` | Buttons and links — the brand red, darkened so white text on it clears WCAG AA |
| `--yellow` | `#B98600` | Accent text, darkened for the same reason |

Swapping the logo means editing one template. If you have the original
vector, replace the paths in `logo_mark.html` and the three `.svg` files.

**Fees are in rupees.** The `money` filter groups digits the Indian way —
`₹1,20,000`, not `₹120,000` — and falls back to thousands grouping for any
other currency. A price of zero renders as "On request" rather than "₹0", so
the corporate plan reads correctly.

---

## The enquiry form

Four fields — name, email, phone, message — because every extra field costs
conversions. Only name and email are required.

**It appears everywhere.** The `{% enquiry_block %}` template tag renders a
self-contained form that can be dropped on any page:

```django
{% enquiry_block course=course heading="Ask us about this course" %}
```

Each block renders its own form instance with its own HTMX target, so several
can sit on one page without interfering.

**Context is captured automatically.** A form on a course page records that
course; one on a teacher page records the teacher; the pricing buttons record
the plan. The admin therefore shows *what* each person asked about, not just
that somebody wrote in. The originating path and referrer are stored too.

**Spam is handled without a captcha:**

- A honeypot field, hidden off-screen and `tabindex="-1"` — bots fill it, people cannot.
- A minimum fill time: anything submitted within 2.5 seconds of page load is rejected.
- Links in the name field are rejected outright.
- A per-IP rate limit (`ENQUIRY_RATE_LIMIT`, default 5 per hour).

Nobody has to identify a bicycle, and no third-party script is loaded.

**It works without JavaScript.** The same POST endpoint returns an HTML
fragment to HTMX, or redirects to `/enquiry/thank-you/` when HTMX is absent.

---

## The admin

`/admin/` is the whole back office.

| Section | What staff manage |
|---------|-------------------|
| **Enquiries** | The inbox: status workflow, internal notes, CSV export |
| Courses | Title, level, format, price, schedule, next start date, syllabus |
| Teachers | Photo, bio, specialisms, qualifications, availability |
| Pricing | Plans and their feature lists |
| Site content | Process steps, testimonials, statistics, FAQs, hero words |

The enquiry inbox is built for actually working leads:

- A **waiting** column that turns amber after a day and red after two, so
  nothing is quietly forgotten.
- Bulk actions: mark contacted, qualified, enrolled or spam.
- **CSV export** of any selection, for a CRM or a spreadsheet.
- Submitted fields are read-only, so the record of what someone actually
  wrote cannot be edited after the fact. Notes go in a separate private field.
- Enquiries cannot be created by hand — they only ever arrive from the form.

---

## The catalogue

Taken from the school's own course posters, so the site and the marketing
material agree.

**Level courses** — ten to twelve weeks, live online, batches capped at eight:

| Level | | Fee |
|-------|--|-----|
| A1 | Beginner — basic vocabulary, everyday conversations, build confidence | ₹6,000 |
| A2 | Elementary — more vocabulary, simple grammar, real-life situations | ₹6,000 |
| B1 | Intermediate — complex sentences, express your opinion, feel more confident | ₹7,500 |
| B2 | Upper intermediate — advanced grammar, fluent communication, career and study ready | ₹8,500 |

**Bundles** (`Plan` records, each linked to the courses it covers):

| Bundle | Fee | |
|--------|-----|--|
| A1 + A2 | ₹10,999 | Best for beginners |
| B1 + B2 | ₹14,999 | Next level |
| A1 to B2 | ₹24,599 | Complete journey |

**Goethe + telc exam preparation**, one course per level: A1 ₹7,999 ·
A2 ₹7,999 · B1 ₹9,599 · B2 ₹11,599.

**Opportunities after learning German** — study in Germany, better jobs,
travel, connecting with people, a brighter future — are `Highlight` records
shown on the homepage and the courses page. The same model drives the trust
strip under the hero (flexible learning, expert guidance, structured
curriculum, lifetime access), so both lists are editable in the admin rather
than baked into a template.

---

## One teacher

The school is one person, so `/teachers/` redirects to her profile rather
than showing a directory of one. Add a second `Teacher` and the list view
comes back automatically — there is a test for both halves of that.

**Her profile is deliberately missing credentials.** `qualifications` is
seeded blank and `years_experience` is left at its default, because
inventing certificates for a named, real person would put a false claim on a
live site. Fill those in from the admin. The seeded bio and specialisms only
describe what the published catalogue already commits to.

For the same reason:

- **The homepage statistics are structural facts** — levels taught, batch
  size, fee floor, reply time. The earlier placeholders ("2,400+ students
  taught", "94% exam pass rate") were invented and are gone. Add real
  figures in the admin once there are real figures.
- **The example testimonials are seeded unpublished.** They are written
  samples under invented names; publishing them as real student feedback
  would be misleading. Replace the text with genuine quotes, then tick
  *is published*.

---

## The map quiz

`/game/germany-map/` asks "Wo ist Hamburg?" and the player clicks a marker on
a 3D map of Germany. Eight questions, hints on request, and a result card
that turns a good score into a course recommendation and a CTA.

- **Cities are managed in the admin** — name, normalised map coordinates, a
  hint, a fun fact and a difficulty. Easy cities are asked first so the
  opening question is winnable.
- **It works without WebGL.** The same round can be played from a list of
  city buttons, which also makes it keyboard- and screen-reader-accessible.
- **Rounds are recorded anonymously** in `GamePlay` — score, duration, hints
  used, nothing personal. The admin changelist header shows how many people
  play and how they do, so you can judge whether it earns its place.
- **Scores are clamped server-side**, so a tampered request cannot record 999
  out of 8.

The same `germany-map.js` module runs in `teaser` mode on the homepage, with
labelled markers and a slow drift, linking through to the game.

---

## HTMX

Used sparingly, only where it removes a page reload:

| Interaction | Endpoint | Swaps |
|-------------|----------|-------|
| Send an enquiry | `POST /enquiry/submit/` | the thank-you panel |
| Validation errors | same, `422` | the form with errors inline |
| Rate limited | same, `429` | the form with an explanation |
| Filter courses | `GET /courses/` | the results grid |
| Filter teachers | `GET /teachers/` | the results grid |
| Finish a quiz round | `POST /game/germany-map/result/` | the score card and CTA |

Views check `request.htmx` and return a fragment or the full page, so every
URL still works on its own.

---

## Front end

| Module | Responsibility |
|--------|----------------|
| `main.js` | Boot, HTMX config, lazy-loads Three.js |
| `forms.js` | Inline validation, double-submit guard, focus management |
| `navigation.js` | Sticky nav, mobile drawer, toasts, modals, FAQ accordion |
| `animations.js` | GSAP entrances and ScrollTrigger reveals |
| `three-hero.js` | The homepage town scene |
| `germany-map.js` | The 3D map, in quiz and teaser modes |
| `map-quiz.js` | The quiz round: questions, scoring, result |
| `utils.js` | DOM helpers, CSRF, capability detection |

### Three.js

Two scenes, both built from primitive geometry — no model files, no textures.

**The homepage town** (`three-hero.js`) has the Brandenburg Gate, a church
with a spire, a station with a moving train, a tram on rails, a market with
striped awnings, a river and bridge, street lamps, drifting clouds and
circling birds. German words orbit above it on two rings at golden-angle
spacing, fading with distance so the far ones recede rather than fighting
the near ones; clicking one shows its meaning. About 4,300 triangles.

**The map of Germany** (`germany-map.js`) is an extruded outline of roughly
forty coordinates with pin markers, used by the quiz and the homepage teaser.

Both load only when the page has the container, it has scrolled near the
viewport, the device supports WebGL, motion is not reduced, and the browser
is not reporting a data-saver connection. Both stop rendering when scrolled
away or the tab is hidden, and mobile gets fewer trees, no shadows, no lamps
and a lower pixel ratio.

When 3D is unavailable a server-rendered fallback appears instead — a word
cloud for the hero, a city list for the map — and the quiz stays playable.

### Motion and accessibility

`prefers-reduced-motion` is honoured in both CSS and JavaScript, and disables
the 3D scene entirely. An inline script in `<head>` sets the flag before first
paint, so nothing flashes in. Semantic landmarks, a skip link, visible focus
rings, labelled fields, `aria-invalid` on failed validation and 56px touch
targets on small screens.

---

## SEO

- Canonical URLs, Open Graph and Twitter tags on every page.
- Per-object `seo_title`, `seo_description`, `og_image` and `noindex`.
- JSON-LD: `EducationalOrganization`, `Course` with `offers`, `Person`,
  `FAQPage`, `BreadcrumbList`.
- `/sitemap.xml` covering every page, course and teacher.
- `/robots.txt` excluding only `/admin/`.

---

## Testing

```bash
python manage.py test          # 83 tests
python manage.py test leads    # the enquiry path on its own
python manage.py test games    # the map quiz
```

Covered: every page renders, unpublished content 404s, every page offers a way
to enquire, the filters return fragments rather than whole documents, course
and teacher attribution, all four spam defences, rate limiting, the no-JS
fallback path, Indian rupee grouping, fee and duration arithmetic, slug
collisions, quiz scoring and server-side clamping of tampered scores, every
admin changelist and add form, the CSV export and bulk actions, and that
seeding twice does not duplicate anything.

The Three.js scenes are additionally checked two ways: every geometry builder
is executed against Three.js in Node with a triangle-budget assertion, and
both pages are rendered in headless Chrome with software WebGL to confirm the
canvas actually initialises and no JavaScript errors are thrown.

---

## Deployment

There is one settings file. It runs in development unless the environment
variable `DJANGO_ENV` is `production`, which switches on the live site at
https://germango.in:

```bash
export DJANGO_ENV=production
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy          # must report no issues
gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3
```

In production, settings turn off `DEBUG`, accept only `germango.in` and
`www.germango.in`, enable HSTS, secure and HTTP-only cookies, and compressed
hashed static files, and trust Cloudflare's `X-Forwarded-Proto` header. The
site is served through a Cloudflare named tunnel, so turn on "Always Use
HTTPS" in the Cloudflare dashboard: Django does not redirect HTTP itself.
`X-Frame-Options: DENY`, nosniff and a strict referrer policy apply in both
modes.

Two things to set before launch:

- **Email** — configure SMTP so enquiry notifications actually arrive, and set
  `ENQUIRY_NOTIFY_EMAILS` to the address that should receive them. In
  development they print to the console.
- **Contact details** — `CONTACT` in settings feeds the navbar, footer and
  every enquiry block. The seeded phone number and Bengaluru address are
  placeholders.

SQLite is fine for a brochure site with a form. If enquiry volume grows enough
to matter, switch `DATABASES` to PostgreSQL — nothing else needs changing.

---

## Management commands

```bash
python manage.py seed_content           # idempotent: safe to re-run
python manage.py seed_content --fresh   # wipe seeded content first
```

Seeds the real catalogue — four level courses and four Goethe/telc
exam-preparation courses with full syllabuses, three bundles, one teacher,
twelve map-quiz cities, five "opportunities", four trust points, four
process steps, twenty FAQs and the homepage statistics. Every fee matches
the course posters. Example testimonials are seeded unpublished.
