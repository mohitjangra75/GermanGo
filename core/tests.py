"""Site-wide tests over the seeded content."""

from django.contrib import admin
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from core.models import Faq, HeroWord, ProcessStep, SiteStat, Testimonial
from courses.models import Course, CourseModule
from leads.models import Enquiry
from pricing.models import Plan
from teachers.models import Teacher

HTMX = {"HTTP_HX_REQUEST": "true"}


class SeededTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_content", verbosity=0)
        cls.course = Course.objects.first()
        cls.teacher = Teacher.objects.first()
        cls.plan = Plan.objects.first()


class PageRenderTests(SeededTestCase):
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
        self.assertEqual(Teacher.objects.published().count(), 1)
        response = self.client.get(reverse("teachers:list"))
        self.assertRedirects(response, Teacher.objects.first().get_absolute_url())

    def test_the_directory_returns_a_list_once_a_second_teacher_exists(self):
        Teacher.objects.create(name="Second Teacher", levels_taught="A1")
        response = self.client.get(reverse("teachers:list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["teachers"]), 2)

    def test_every_course_page_renders(self):
        for course in Course.objects.all():
            with self.subTest(course=course.title):
                response = self.client.get(course.get_absolute_url())
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, course.title)

    def test_every_teacher_page_renders(self):
        for teacher in Teacher.objects.all():
            with self.subTest(teacher=teacher.name):
                response = self.client.get(teacher.get_absolute_url())
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, teacher.name)

    def test_an_unpublished_course_is_404(self):
        self.course.is_published = False
        self.course.save()
        self.assertEqual(self.client.get(self.course.get_absolute_url()).status_code, 404)

    def test_an_unpublished_teacher_is_404(self):
        self.teacher.is_published = False
        self.teacher.save()
        self.assertEqual(self.client.get(self.teacher.get_absolute_url()).status_code, 404)

    def test_the_homepage_carries_its_headline_and_metadata(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "Learn German.")
        self.assertContains(response, "Speak with Confidence.")
        self.assertContains(response, 'rel="canonical"')
        self.assertContains(response, "application/ld+json")

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


class FilterTests(SeededTestCase):
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
        response = self.client.get(reverse("courses:list"), {"format": "private"})
        for course in response.context["courses"]:
            self.assertEqual(course.course_format, "private")

    def test_an_unknown_level_is_ignored(self):
        response = self.client.get(reverse("courses:list"), {"level": "ZZ"})
        self.assertEqual(response.context["total"], Course.objects.published().count())

    def test_teacher_filters_return_a_fragment(self):
        self.assert_is_fragment(
            self.client.get(reverse("teachers:list"), {"level": "B2"}, **HTMX)
        )

    def test_the_availability_filter_works(self):
        # A second teacher keeps the directory on the list view.
        Teacher.objects.create(name="Spare Teacher", levels_taught="A1")
        self.teacher.is_accepting_students = False
        self.teacher.save()
        response = self.client.get(reverse("teachers:list"), {"available": "1"})
        self.assertNotIn(self.teacher, list(response.context["teachers"]))

    def test_a_normal_request_still_returns_the_full_page(self):
        response = self.client.get(reverse("courses:list"), {"level": "A1"})
        self.assertContains(response, "<!DOCTYPE html>")


class ModelTests(SeededTestCase):
    def test_total_hours_is_computed(self):
        course = Course.objects.create(
            title="Test", level_code="A1", duration_weeks=10, hours_per_week=3
        )
        self.assertEqual(course.total_hours, 30)

    def test_price_per_hour_is_computed(self):
        course = Course.objects.create(
            title="Test 2", level_code="A1", duration_weeks=10, hours_per_week=3, price=300
        )
        self.assertEqual(course.price_per_hour, 10.0)

    def test_price_per_hour_is_none_when_free(self):
        course = Course.objects.create(title="Test 3", level_code="A1", price=0)
        self.assertIsNone(course.price_per_hour)

    def test_one_to_one_is_detected(self):
        course = Course.objects.create(title="Test 4", level_code="A1", max_class_size=1)
        self.assertTrue(course.is_one_to_one)

    def test_line_fields_become_lists(self):
        course = Course.objects.create(
            title="Test 5", level_code="A1", outcomes="One\n\nTwo\n  Three  "
        )
        self.assertEqual(course.outcome_list, ["One", "Two", "Three"])

    def test_teacher_comma_fields_become_lists(self):
        teacher = Teacher.objects.create(
            name="Test Teacher", languages="German, English , Spanish", levels_taught="A1,B2"
        )
        self.assertEqual(teacher.language_list, ["German", "English", "Spanish"])
        self.assertEqual(teacher.level_list, ["A1", "B2"])

    def test_teacher_initials(self):
        self.assertEqual(Teacher(name="Anna Weber").initials, "AW")
        self.assertEqual(Teacher(name="Anna").initials, "AN")

    def test_slugs_are_generated_and_unique(self):
        first = Course.objects.create(title="Duplicate Name", level_code="A1")
        second = Course.objects.create(title="Duplicate Name", level_code="A2")
        self.assertEqual(first.slug, "duplicate-name")
        self.assertEqual(second.slug, "duplicate-name-2")


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

    def test_file_url_survives_an_empty_field(self):
        from core.templatetags.germango import file_url

        self.assertEqual(file_url(None), "")
        self.assertEqual(file_url(Teacher(name="X").photo), "")


class AdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_content", verbosity=0)
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


class SeedCommandTests(TestCase):
    def test_seeding_twice_does_not_duplicate(self):
        call_command("seed_content", verbosity=0)
        before = [
            Course.objects.count(), CourseModule.objects.count(),
            Teacher.objects.count(), Plan.objects.count(),
            Faq.objects.count(), Testimonial.objects.count(),
            SiteStat.objects.count(), ProcessStep.objects.count(),
            HeroWord.objects.count(),
        ]
        call_command("seed_content", verbosity=0)
        after = [
            Course.objects.count(), CourseModule.objects.count(),
            Teacher.objects.count(), Plan.objects.count(),
            Faq.objects.count(), Testimonial.objects.count(),
            SiteStat.objects.count(), ProcessStep.objects.count(),
            HeroWord.objects.count(),
        ]
        self.assertEqual(before, after)

    def test_fresh_rebuilds_cleanly(self):
        call_command("seed_content", verbosity=0)
        call_command("seed_content", "--fresh", verbosity=0)
        self.assertTrue(Course.objects.exists())
        self.assertTrue(Teacher.objects.exists())
