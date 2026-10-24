"""Root URL configuration.

Every path is named and namespaced; templates never hard-code a URL.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path
from django.views.static import serve

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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Uploaded photos have to load on the tunnelled preview too, where DEBUG
    # is off and `static()` above returns nothing. Django serves them itself
    # here; on a permanent host, hand /media/ to the web server instead.
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}
        ),
    ]
