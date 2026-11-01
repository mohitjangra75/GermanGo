"""Map quiz tests."""

from unittest import mock

from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from games.content import CITIES, EASY, City
from games.views import Round

HTMX = {"HTTP_HX_REQUEST": "true"}


class CityTests(SimpleTestCase):
    def test_the_payload_has_what_the_scene_needs(self):
        city = City("Düsseldorf", "Nordrhein-Westfalen", -0.58, -0.04, EASY, 619294,
                    "#2F5D8C", hint="West.", fact="A fact.")
        payload = city.as_payload()
        self.assertEqual(payload["slug"], "dusseldorf")
        self.assertEqual(payload["x"], -0.58)
        self.assertEqual(payload["z"], -0.04)
        self.assertEqual(payload["hint"], "West.")

    def test_coordinates_stay_on_the_map(self):
        for city in CITIES:
            with self.subTest(city=city.name):
                self.assertTrue(-1 <= city.x <= 1 and -1 <= city.z <= 1)


class QuizPageTests(TestCase):
    def test_the_page_renders_with_its_cities(self):
        response = self.client.get(reverse("games:map_quiz"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data-germany-map")
        self.assertContains(response, 'data-mode="quiz"')
        self.assertContains(response, "Berlin")

    def test_the_round_is_capped_at_the_number_of_cities(self):
        with mock.patch("games.views.CITIES", CITIES[:2]):
            response = self.client.get(reverse("games:map_quiz"))
        self.assertEqual(response.context["round_length"], 2)

    def test_the_page_offers_a_way_to_enquire(self):
        response = self.client.get(reverse("games:map_quiz"))
        self.assertContains(response, reverse("leads:submit"))

    def test_the_homepage_teaser_is_present(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, 'data-mode="teaser"')
        self.assertContains(response, reverse("games:map_quiz"))

    def test_the_quiz_page_does_not_leak_answers_as_labels(self):
        """Markers must stay unlabelled in quiz mode, or it is not a quiz."""
        response = self.client.get(reverse("games:map_quiz"))
        self.assertNotContains(response, 'data-mode="teaser"')


class ResultTests(TestCase):
    """Results are never saved; the only query is reading the course links."""

    def url(self):
        return reverse("games:map_quiz_result")

    def post(self, data, **extra):
        return self.client.post(self.url(), data, **extra)

    def test_a_finished_round_gets_a_result(self):
        response = self.post(
            {"score": "6", "total": "8", "seconds": "94", "hints": "1"}, **HTMX
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["play"], Round(score=6, total=8, seconds=94, used_hints=1)
        )
        self.assertContains(response, "75% in 94 seconds")

    def test_the_result_card_shows_the_score_and_a_cta(self):
        response = self.client.post(
            self.url(), {"score": "8", "total": "8", "seconds": "60"}, **HTMX
        )
        self.assertContains(response, "8")
        self.assertContains(response, "Perfekt!")
        self.assertContains(response, reverse("leads:enquiry"))

    def test_a_round_saves_nothing(self):
        with self.assertNumQueries(1):
            self.post({"score": "6", "total": "8"}, **HTMX)

    def test_the_verdict_matches_the_score(self):
        for score, expected in [(8, "Perfekt!"), (7, "Sehr gut!"), (5, "Nicht schlecht!"), (0, "Übung")]:
            play = Round(score=score, total=8)
            self.assertIn(expected, play.verdict, msg=f"score {score}")

    def test_a_score_above_the_total_is_clamped(self):
        """A tampered payload must not produce an impossible score."""
        response = self.post({"score": "999", "total": "8"}, **HTMX)
        self.assertEqual(response.context["play"].score, 8)

    def test_a_negative_score_is_clamped(self):
        response = self.post({"score": "-5", "total": "8"}, **HTMX)
        self.assertEqual(response.context["play"].score, 0)

    def test_an_absurd_total_is_clamped(self):
        response = self.post({"score": "10", "total": "100000"}, **HTMX)
        self.assertEqual(response.context["play"].total, 50)

    def test_non_numeric_input_is_rejected(self):
        response = self.post({"score": "abc", "total": "8"}, **HTMX)
        self.assertEqual(response.status_code, 400)

    def test_an_empty_round_is_rejected(self):
        response = self.post({"score": "0", "total": "0"}, **HTMX)
        self.assertEqual(response.status_code, 400)

    def test_get_is_not_allowed(self):
        self.assertEqual(self.client.get(self.url()).status_code, 405)

    def test_a_non_htmx_post_redirects_back_to_the_game(self):
        response = self.post({"score": "4", "total": "8"})
        self.assertRedirects(response, reverse("games:map_quiz"))

    def test_percent_is_zero_for_an_empty_round(self):
        self.assertEqual(Round(score=0, total=0).percent, 0)
