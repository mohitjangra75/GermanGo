from django.urls import path

from . import views

app_name = "games"

urlpatterns = [
    path("germany-map/", views.map_quiz, name="map_quiz"),
    path("germany-map/result/", views.map_quiz_result, name="map_quiz_result"),
]
