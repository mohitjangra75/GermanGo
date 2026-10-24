"""Map quiz tests."""

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from games.models import GamePlay, MapCity

HTMX = {"HTTP_HX_REQUEST": "true"}


class MapCityTests(TestCase):
    def test_the_payload_has_what_the_scene_needs(self):
        city = MapCity.objects.create(
            name="Berlin", state="Berlin", map_x=0.42, map_z=-0.42, hint="North-east."
        )
        payload = city.as_payload()
        self.assertEqual(payload["slug"], "berlin")
        self.assertEqual(payload["x"], 0.42)
        self.assertEqual(payload["z"], -0.42)
        self.assertEqual(payload["hint"], "North-east.")

    def test_unpublished_cities_are_left_out(self):
        MapCity.objects.create(name="Berlin", map_x=0, map_z=0)
        MapCity.objects.create(name="Hidden", map_x=0, map_z=0, is_published=False)
        self.assertEqual(MapCity.objects.published().count(), 1)


class QuizPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_content", verbosity=0)

    def test_the_page_renders_with_its_cities(self):
        response = self.client.get(reverse("games:map_quiz"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data-germany-map")
        self.assertContains(response, 'data-mode="quiz"')
        self.assertContains(response, "Berlin")

    def test_the_round_is_capped_at_the_number_of_cities(self):
        MapCity.objects.exclude(name__in=["Berlin", "Munich"]).delete()
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
    @classmethod
    def setUpTestData(cls):
        call_command("seed_content", verbosity=0)

    def url(self):
        return reverse("games:map_quiz_result")

    def test_a_finished_round_is_recorded(self):
        response = self.client.post(
            self.url(), {"score": "6", "total": "8", "seconds": "94", "hints": "1"}, **HTMX
        )
        self.assertEqual(response.status_code, 200)

        play = GamePlay.objects.get()
        self.assertEqual(play.score, 6)
        self.assertEqual(play.total, 8)
        self.assertEqual(play.seconds, 94)
        self.assertEqual(play.used_hints, 1)
        self.assertEqual(play.percent, 75)

    def test_the_result_card_shows_the_score_and_a_cta(self):
        response = self.client.post(
            self.url(), {"score": "8", "total": "8", "seconds": "60"}, **HTMX
        )
        self.assertContains(response, "8")
        self.assertContains(response, "Perfekt!")
        self.assertContains(response, reverse("leads:enquiry"))

    def test_the_verdict_matches_the_score(self):
        for score, expected in [(8, "Perfekt!"), (7, "Sehr gut!"), (5, "Nicht schlecht!"), (0, "Übung")]:
            play = GamePlay(score=score, total=8)
            self.assertIn(expected, play.verdict, msg=f"score {score}")

    def test_a_score_above_the_total_is_clamped(self):
        """A tampered payload must not produce an impossible score."""
        self.client.post(self.url(), {"score": "999", "total": "8"}, **HTMX)
        self.assertEqual(GamePlay.objects.get().score, 8)

    def test_a_negative_score_is_clamped(self):
        self.client.post(self.url(), {"score": "-5", "total": "8"}, **HTMX)
        self.assertEqual(GamePlay.objects.get().score, 0)

    def test_an_absurd_total_is_clamped(self):
        self.client.post(self.url(), {"score": "10", "total": "100000"}, **HTMX)
        self.assertEqual(GamePlay.objects.get().total, 50)

    def test_non_numeric_input_is_rejected(self):
        response = self.client.post(self.url(), {"score": "abc", "total": "8"}, **HTMX)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(GamePlay.objects.exists())

    def test_an_empty_round_is_rejected(self):
        response = self.client.post(self.url(), {"score": "0", "total": "0"}, **HTMX)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(GamePlay.objects.exists())

    def test_get_is_not_allowed(self):
        self.assertEqual(self.client.get(self.url()).status_code, 405)

    def test_a_non_htmx_post_redirects_back_to_the_game(self):
        response = self.client.post(self.url(), {"score": "4", "total": "8"})
        self.assertRedirects(response, reverse("games:map_quiz"))
        self.assertTrue(GamePlay.objects.exists())

    def test_percent_is_zero_for_an_empty_round(self):
        self.assertEqual(GamePlay(score=0, total=0).percent, 0)
