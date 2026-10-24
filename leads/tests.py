"""Enquiry capture tests — the conversion path must never break silently."""

import time

from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from courses.models import Course
from leads.models import Enquiry
from pricing.models import Plan
from teachers.models import Teacher

HTMX = {"HTTP_HX_REQUEST": "true"}


class EnquiryTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.course = Course.objects.create(
            title="German A1 — Evening Group", level_code="A1", price=390
        )
        cls.teacher = Teacher.objects.create(name="Anna Weber")
        cls.plan = Plan.objects.create(name="Evening Group", price=130)

    def setUp(self):
        cache.clear()
        mail.outbox = []

    def payload(self, **overrides):
        data = {
            "name": "Priya Raghavan",
            "email": "Priya@Example.Test",
            "phone": "+49 170 1234567",
            "message": "I am a complete beginner and would like to start in March.",
            "website": "",
            # A real person took longer than the minimum to fill the form in.
            "loaded_at": str(time.time() - 30),
            "form_id": "home",
            "source_path": "/",
        }
        data.update(overrides)
        return data

    def post(self, **overrides):
        return self.client.post(reverse("leads:submit"), self.payload(**overrides), **HTMX)


class SubmissionTests(EnquiryTestCase):
    def test_a_valid_enquiry_is_saved(self):
        response = self.post()
        self.assertEqual(response.status_code, 200)

        enquiry = Enquiry.objects.get()
        self.assertEqual(enquiry.name, "Priya Raghavan")
        self.assertEqual(enquiry.email, "priya@example.test")  # normalised
        self.assertEqual(enquiry.phone, "+49 170 1234567")
        self.assertEqual(enquiry.status, Enquiry.Status.NEW)

    def test_the_visitor_sees_a_thank_you(self):
        response = self.post()
        self.assertContains(response, "Danke")
        self.assertContains(response, "one working day")

    def test_only_the_name_and_phone_are_required(self):
        self.post(email="", message="")
        enquiry = Enquiry.objects.get()
        self.assertEqual(enquiry.email, "")
        self.assertEqual(enquiry.message, "")

    def test_the_team_is_emailed(self):
        self.post()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Priya Raghavan", mail.outbox[0].subject)
        self.assertIn("priya@example.test", mail.outbox[0].body)

    def test_the_source_page_is_recorded(self):
        self.post(source_path="/courses/german-a1-evening-group/")
        self.assertEqual(
            Enquiry.objects.get().source_path, "/courses/german-a1-evening-group/"
        )

    def test_a_missing_name_is_rejected(self):
        response = self.post(name="")
        self.assertEqual(response.status_code, 422)
        self.assertFalse(Enquiry.objects.exists())

    def test_a_missing_phone_is_rejected(self):
        response = self.post(phone="")
        self.assertEqual(response.status_code, 422)
        self.assertFalse(Enquiry.objects.exists())

    def test_a_phone_without_enough_digits_is_rejected(self):
        response = self.post(phone="call me")
        self.assertEqual(response.status_code, 422)
        self.assertFalse(Enquiry.objects.exists())

    def test_a_malformed_email_is_rejected(self):
        response = self.post(email="not-an-email")
        self.assertEqual(response.status_code, 422)
        self.assertFalse(Enquiry.objects.exists())

    def test_the_form_is_returned_with_its_errors(self):
        response = self.post(email="nope")
        self.assertContains(response, "Send enquiry", status_code=422)
        self.assertContains(response, "field--invalid", status_code=422)

    def test_a_get_redirects_to_the_enquiry_page(self):
        response = self.client.get(reverse("leads:submit"))
        self.assertRedirects(response, reverse("leads:enquiry"))


class ContextTests(EnquiryTestCase):
    def test_a_course_enquiry_is_attributed(self):
        self.post(course=self.course.slug)
        enquiry = Enquiry.objects.get()
        self.assertEqual(enquiry.course, self.course)
        self.assertIn(self.course.title, enquiry.interest)

    def test_a_teacher_enquiry_is_attributed(self):
        self.post(teacher=self.teacher.slug)
        self.assertEqual(Enquiry.objects.get().teacher, self.teacher)

    def test_a_plan_enquiry_is_attributed(self):
        self.post(plan=str(self.plan.pk))
        self.assertEqual(Enquiry.objects.get().plan, self.plan)

    def test_an_unknown_course_is_ignored_rather_than_failing(self):
        response = self.post(course="no-such-course")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(Enquiry.objects.get().course)

    def test_a_non_numeric_plan_id_is_ignored(self):
        response = self.post(plan="../../etc/passwd")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(Enquiry.objects.get().plan)

    def test_an_unpublished_course_is_not_attached(self):
        self.course.is_published = False
        self.course.save()
        self.post(course=self.course.slug)
        self.assertIsNone(Enquiry.objects.get().course)

    def test_the_thank_you_names_the_course(self):
        response = self.post(course=self.course.slug)
        self.assertContains(response, self.course.title)


class SpamTests(EnquiryTestCase):
    def test_a_filled_honeypot_is_rejected(self):
        response = self.post(website="https://buy-cheap-things.example")
        self.assertEqual(response.status_code, 422)
        self.assertFalse(Enquiry.objects.exists())

    def test_an_instant_submission_is_rejected(self):
        response = self.post(loaded_at=str(time.time()))
        self.assertEqual(response.status_code, 422)
        self.assertFalse(Enquiry.objects.exists())

    def test_a_link_in_the_name_field_is_rejected(self):
        response = self.post(name="Cheap deals https://spam.example")
        self.assertEqual(response.status_code, 422)
        self.assertFalse(Enquiry.objects.exists())

    def test_a_one_character_name_is_rejected(self):
        response = self.post(name="x")
        self.assertEqual(response.status_code, 422)
        self.assertFalse(Enquiry.objects.exists())

    def test_a_missing_timestamp_does_not_block_a_real_person(self):
        """A stripped hidden field must not lock a genuine visitor out."""
        response = self.post(loaded_at="")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Enquiry.objects.exists())

    @override_settings(ENQUIRY_RATE_LIMIT=3)
    def test_an_ip_is_throttled_after_the_limit(self):
        for index in range(3):
            response = self.post(email=f"person{index}@example.test")
            self.assertEqual(response.status_code, 200)

        response = self.post(email="flood@example.test")
        self.assertEqual(response.status_code, 429)
        self.assertContains(response, "several enquiries", status_code=429)
        self.assertEqual(Enquiry.objects.count(), 3)


class NoJavaScriptTests(EnquiryTestCase):
    """The form must work when HTMX never loads."""

    def test_a_plain_post_redirects_to_the_thank_you_page(self):
        response = self.client.post(reverse("leads:submit"), self.payload())
        self.assertRedirects(response, reverse("leads:thanks"))
        self.assertTrue(Enquiry.objects.exists())

    def test_a_plain_post_with_errors_re_renders_the_page(self):
        response = self.client.post(reverse("leads:submit"), self.payload(phone=""))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Send enquiry")
        self.assertFalse(Enquiry.objects.exists())


class ModelTests(EnquiryTestCase):
    def test_interest_falls_back_to_a_general_label(self):
        enquiry = Enquiry.objects.create(name="A", email="a@example.test")
        self.assertEqual(enquiry.interest, "General enquiry")

    def test_marking_contacted_sets_the_timestamp(self):
        enquiry = Enquiry.objects.create(name="A", email="a@example.test")
        enquiry.mark_contacted()
        enquiry.refresh_from_db()
        self.assertEqual(enquiry.status, Enquiry.Status.CONTACTED)
        self.assertIsNotNone(enquiry.contacted_at)

    def test_marking_contacted_twice_keeps_the_first_timestamp(self):
        enquiry = Enquiry.objects.create(name="A", email="a@example.test")
        enquiry.mark_contacted()
        first = enquiry.contacted_at
        enquiry.mark_contacted()
        self.assertEqual(enquiry.contacted_at, first)
