"""Site-wide tests over the course catalogue and each app's content.py."""

from dataclasses import replace
from unittest import mock

from django.contrib import admin
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from core.content import FAQS, TESTIMONIALS
from courses.models import Course
from games.content import CITIES
from leads.models import Enquiry
from pricing.content import PLANS
from teachers.content import TEACHERS, Teacher

HTMX = {"HTTP_HX_REQUEST": "true"}


class ContentTestCase(TestCase):
    # The catalogue is loaded by courses/migrations/0006_load_courses.py.
    teacher = TEACHERS[0]
    plan = PLANS[0]

    @classmethod
    def setUpTestData(cls):
        cls.course = Course.objects.published().first()


class PageRenderTests(ContentTestCase):
    def test_every_page_renders(self):
        pages = [
            reverse("core:home"),
            reverse("core:process"),
            reverse("courses:list"),
            reverse("teachers:list"),
            reverse("pricing:index"),
            reverse("leads:enquiry"),
            reverse("leads:thanks"),
            reverse("robots"),
            reverse("sitemap"),
        ]
        for url in pages:
            with self.subTest(url=url):
                # /teachers/ redirects to the profile while there is one
                # teacher, so follow rather than asserting 200 outright.
                self.assertEqual(self.client.get(url, follow=True).status_code, 200)

    def test_the_teacher_directory_redirects_while_there_is_one_teacher(self):
        self.assertEqual(len(TEACHERS), 1)
        response = self.client.get(reverse("teachers:list"))
        self.assertRedirects(response, TEACHERS[0].get_absolute_url())

    def test_the_directory_returns_a_list_once_a_second_teacher_exists(self):
        second = Teacher(slug="second-teacher", name="Second Teacher", levels=["A1"])
        with mock.patch("teachers.views.TEACHERS", [self.teacher, second]):
            response = self.client.get(reverse("teachers:list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["teachers"]), 2)

    def test_every_course_page_renders(self):
        for course in Course.objects.published():
            with self.subTest(course=course.title):
                response = self.client.get(course.get_absolute_url())
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, course.title)

    def test_every_teacher_page_renders(self):
        for teacher in TEACHERS:
            with self.subTest(teacher=teacher.name):
                response = self.client.get(teacher.get_absolute_url())
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, teacher.name)

    def test_an_unknown_course_is_404(self):
        url = reverse("courses:detail", kwargs={"slug": "no-such-course"})
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_an_unpublished_course_is_404(self):
        Course.objects.filter(pk=self.course.pk).update(is_published=False)
        self.assertEqual(self.client.get(self.course.get_absolute_url()).status_code, 404)

    def test_an_unknown_teacher_is_404(self):
        url = reverse("teachers:detail", kwargs={"slug": "no-such-teacher"})
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_the_homepage_carries_its_headline_and_metadata(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "Learn German.")
        self.assertContains(response, "Speak with Confidence.")
        self.assertContains(response, 'rel="canonical" href="http://localhost:8000/"')
        self.assertContains(response, 'property="og:url" content="http://localhost:8000/"')
        self.assertContains(response, "application/ld+json")

    def test_reviews_show_on_the_homepage_and_their_course_page(self):
        home = self.client.get(reverse("core:home"))
        for item in TESTIMONIALS[:3]:
            self.assertContains(home, item.name)
        for item in TESTIMONIALS:
            if item.course:
                page = self.client.get(Course.objects.get(slug=item.course).get_absolute_url())
                self.assertContains(page, item.name)

    def test_the_canonical_url_uses_site_domain_whichever_host_served_it(self):
        url = self.course.get_absolute_url()
        with self.settings(
            SITE_DOMAIN="germango.in",
            SITE_PROTOCOL="https",
            ALLOWED_HOSTS=["germango.in", "www.germango.in"],
        ):
            response = self.client.get(url, HTTP_HOST="www.germango.in")
        self.assertContains(response, f'rel="canonical" href="https://germango.in{url}"')

    def test_a_course_page_shows_its_fee_and_syllabus(self):
        from core.templatetags.germango import money

        response = self.client.get(self.course.get_absolute_url())
        self.assertContains(response, money(self.course.price, self.course.currency))
        for module in self.course.modules.all():
            self.assertContains(response, module.title)

    def test_fees_are_shown_in_rupees(self):
        response = self.client.get(reverse("pricing:index"))
        self.assertContains(response, "₹")
        self.assertNotContains(response, "€")

    def test_every_page_offers_a_way_to_enquire(self):
        """The conversion goal must be reachable from anywhere."""
        pages = [
            reverse("core:home"),
            reverse("core:process"),
            reverse("courses:list"),
            reverse("teachers:list"),
            reverse("pricing:index"),
            self.course.get_absolute_url(),
            self.teacher.get_absolute_url(),
        ]
        for url in pages:
            with self.subTest(url=url):
                response = self.client.get(url, follow=True)
                self.assertContains(response, reverse("leads:submit"))


class FilterTests(ContentTestCase):
    def assert_is_fragment(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"<!DOCTYPE html>", response.content)
        self.assertNotIn(b"<body", response.content)

    def test_course_level_filter_returns_a_fragment(self):
        response = self.client.get(reverse("courses:list"), {"level": "A1"}, **HTMX)
        self.assert_is_fragment(response)

    def test_course_level_filter_narrows_the_results(self):
        response = self.client.get(reverse("courses:list"), {"level": "B2"})
        for course in response.context["courses"]:
            self.assertEqual(course.level_code, "B2")

    def test_course_format_filter_narrows_the_results(self):
        response = self.client.get(reverse("courses:list"), {"format": "exam"})
        self.assertTrue(response.context["courses"])
        for course in response.context["courses"]:
            self.assertEqual(course.course_format, "exam")

    def test_an_unknown_level_is_ignored(self):
        response = self.client.get(reverse("courses:list"), {"level": "ZZ"})
        self.assertEqual(response.context["total"], Course.objects.published().count())

    def test_teacher_filters_return_a_fragment(self):
        self.assert_is_fragment(
            self.client.get(reverse("teachers:list"), {"level": "B2"}, **HTMX)
        )

    def test_the_availability_filter_works(self):
        # A second teacher keeps the directory on the list view.
        spare = Teacher(slug="spare-teacher", name="Spare Teacher", levels=["A1"])
        full = replace(self.teacher, is_accepting_students=False)
        with mock.patch("teachers.views.TEACHERS", [full, spare]):
            response = self.client.get(reverse("teachers:list"), {"available": "1"})
        self.assertEqual(response.context["teachers"], [spare])

    def test_a_normal_request_still_returns_the_full_page(self):
        response = self.client.get(reverse("courses:list"), {"level": "A1"})
        self.assertContains(response, "<!DOCTYPE html>")


class CatalogueTests(TestCase):
    """Plans and testimonials in code name courses from the database."""

    def test_the_catalogue_is_loaded(self):
        self.assertEqual(Course.objects.published().count(), 8)

    def test_every_course_names_real_teachers(self):
        slugs = {teacher.slug for teacher in TEACHERS}
        for course in Course.objects.all():
            with self.subTest(course=course.slug):
                self.assertTrue(set(course.teacher_slugs) <= slugs)

    def test_every_plan_names_real_courses(self):
        slugs = set(Course.objects.published().values_list("slug", flat=True))
        for plan in PLANS:
            with self.subTest(plan=plan.slug):
                self.assertTrue(plan.course_slugs)
                self.assertTrue(set(plan.course_slugs) <= slugs)

    def test_every_testimonial_names_a_real_course(self):
        slugs = set(Course.objects.published().values_list("slug", flat=True))
        for item in TESTIMONIALS:
            if item.course:
                self.assertIn(item.course, slugs)


class ContentTests(SimpleTestCase):
    """Content is edited by hand, so catch broken references before deploy."""

    def assert_unique(self, slugs):
        self.assertEqual(len(slugs), len(set(slugs)), slugs)

    def test_slugs_are_unique(self):
        self.assert_unique([teacher.slug for teacher in TEACHERS])
        self.assert_unique([plan.slug for plan in PLANS])
        self.assert_unique([city.slug for city in CITIES])

    def test_every_faq_page_has_questions(self):
        for page, faqs in FAQS.items():
            with self.subTest(page=page):
                self.assertTrue(faqs)

    def test_plan_periods_are_known(self):
        for plan in PLANS:
            plan.get_period_display()

    def test_total_hours_is_computed(self):
        course = Course(title="Test", duration_weeks=10, hours_per_week=3)
        self.assertEqual(course.total_hours, 30)

    def test_price_per_hour_is_computed(self):
        course = Course(title="Test", price=300, duration_weeks=10, hours_per_week=3)
        self.assertEqual(course.price_per_hour, 10.0)

    def test_price_per_hour_is_none_when_free(self):
        self.assertIsNone(Course(title="Test", price=0).price_per_hour)

    def test_one_to_one_is_detected(self):
        self.assertTrue(Course(title="Test", max_class_size=1).is_one_to_one)

    def test_line_fields_become_lists(self):
        course = Course(title="Test", outcomes="One\n\nTwo\n  Three  ")
        self.assertEqual(course.outcome_list, ["One", "Two", "Three"])

    def test_a_course_lists_its_teachers(self):
        course = Course(title="Test", teacher_slugs=[TEACHERS[0].slug, "nobody"])
        self.assertEqual(course.teachers, [TEACHERS[0]])

    def test_teacher_initials(self):
        self.assertEqual(Teacher(slug="a", name="Anna Weber").initials, "AW")
        self.assertEqual(Teacher(slug="a", name="Anna").initials, "AN")

    def test_a_teacher_photo_is_a_static_file(self):
        with_photo = next(teacher for teacher in TEACHERS if teacher.photo)
        self.assertTrue(with_photo.photo_url.startswith("/static/"))
        self.assertEqual(Teacher(slug="a", name="Anna").photo_url, "")


class TemplateTagTests(TestCase):
    def test_money_uses_indian_grouping_for_rupees(self):
        """Rupees group by lakh: 1,20,000 rather than 120,000."""
        from core.templatetags.germango import money

        self.assertEqual(money(950, "INR"), "₹950")
        self.assertEqual(money(18000, "INR"), "₹18,000")
        self.assertEqual(money(120000, "INR"), "₹1,20,000")
        self.assertEqual(money(1250000, "INR"), "₹12,50,000")
        self.assertEqual(money(1200.5, "INR"), "₹1,200.50")

    def test_money_uses_thousands_grouping_elsewhere(self):
        from core.templatetags.germango import money

        self.assertEqual(money(1250, "EUR"), "€1,250")
        self.assertEqual(money(120000, "EUR"), "€120,000")
        self.assertEqual(money(100, "GBP"), "£100")

    def test_money_handles_rubbish_input(self):
        from core.templatetags.germango import money

        self.assertEqual(money(None), "")
        self.assertEqual(money("not a number"), "")


class AdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_superuser(
            username="admin", email="admin@example.test", password="AdminPass!2345"
        )

    def setUp(self):
        self.client.force_login(self.staff)

    def test_the_index_loads(self):
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "GermanGo")

    def test_every_changelist_loads(self):
        for model in admin.site._registry:
            url = reverse(
                f"admin:{model._meta.app_label}_{model._meta.model_name}_changelist"
            )
            with self.subTest(model=model.__name__):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_every_add_form_loads(self):
        for model, model_admin in admin.site._registry.items():
            if not model_admin.has_add_permission(
                type("R", (), {"user": self.staff, "method": "GET"})()
            ):
                continue
            url = reverse(f"admin:{model._meta.app_label}_{model._meta.model_name}_add")
            with self.subTest(model=model.__name__):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_a_course_can_be_added_with_its_syllabus(self):
        response = self.client.post(
            reverse("admin:courses_course_add"),
            {
                "title": "German C1 — Advanced",
                "slug": "german-c1-advanced",
                "level_code": "C1",
                "course_format": "group",
                "delivery": "online",
                "duration_weeks": "12",
                "hours_per_week": "3",
                "max_class_size": "8",
                "price": "9999",
                "currency": "INR",
                "teacher_slugs": [TEACHERS[0].slug],
                "accent_color": "#9B2226",
                "order": "9",
                "is_published": "on",
                "modules-TOTAL_FORMS": "1",
                "modules-INITIAL_FORMS": "0",
                "modules-0-order": "0",
                "modules-0-week_range": "Weeks 1–3",
                "modules-0-title": "Nuance",
                "modules-0-topics": "Idioms\nRegister",
            },
        )
        self.assertEqual(response.status_code, 302, getattr(response, "context", None))
        course = Course.objects.get(slug="german-c1-advanced")
        self.assertEqual(course.teacher_slugs, [TEACHERS[0].slug])
        self.assertEqual(course.modules.get().topic_list, ["Idioms", "Register"])
        self.assertContains(self.client.get(course.get_absolute_url()), "Nuance")

    def test_enquiries_cannot_be_added_by_hand(self):
        url = reverse("admin:leads_enquiry_add")
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_the_enquiry_csv_export_works(self):
        enquiry = Enquiry.objects.create(
            name="Priya", email="priya@example.test", message="Hello"
        )
        response = self.client.post(
            reverse("admin:leads_enquiry_changelist"),
            {"action": "export_csv", "_selected_action": [str(enquiry.pk)]},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn(b"priya@example.test", response.content)

    def test_the_bulk_contacted_action_works(self):
        enquiry = Enquiry.objects.create(name="Priya", email="priya@example.test")
        self.client.post(
            reverse("admin:leads_enquiry_changelist"),
            {"action": "mark_contacted", "_selected_action": [str(enquiry.pk)]},
        )
        enquiry.refresh_from_db()
        self.assertEqual(enquiry.status, Enquiry.Status.CONTACTED)
        self.assertIsNotNone(enquiry.contacted_at)

    def test_the_admin_requires_staff(self):
        self.client.logout()
        learner = User.objects.create_user(
            username="visitor", email="v@example.test", password="VisitorPass!2345"
        )
        self.client.force_login(learner)
        self.assertEqual(self.client.get(reverse("admin:index")).status_code, 302)
