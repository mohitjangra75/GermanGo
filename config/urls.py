"""Root URL configuration.

Every path is named and namespaced; templates never hard-code a URL.
"""

from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from core.sitemaps import SITEMAPS
from core.views import robots_txt

urlpatterns = [
    path("admin/", admin.site.urls),
    path("courses/", include("courses.urls")),
    path("teachers/", include("teachers.urls")),
    path("pricing/", include("pricing.urls")),
    path("game/", include("games.urls")),
    path("enquiry/", include("leads.urls")),
    path("robots.txt", robots_txt, name="robots"),
    path("sitemap.xml", sitemap, {"sitemaps": SITEMAPS}, name="sitemap"),
    # Home last so its patterns never shadow a section.
    path("", include("core.urls")),
]
