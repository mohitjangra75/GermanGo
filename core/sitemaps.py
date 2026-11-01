"""Sitemap classes wired into /sitemap.xml."""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from courses.models import Course
from teachers.content import TEACHERS


class StaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1.0

    def items(self):
        return [
            "core:home",
            "core:process",
            "courses:list",
            "teachers:list",
            "pricing:index",
            "games:map_quiz",
            "leads:enquiry",
        ]

    def location(self, item):
        return reverse(item)


class CourseSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Course.objects.published()

    def lastmod(self, obj):
        return obj.updated_at


class TeacherSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return TEACHERS


SITEMAPS = {
    "static": StaticSitemap,
    "courses": CourseSitemap,
    "teachers": TeacherSitemap,
}
