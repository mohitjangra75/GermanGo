from django.urls import path

from . import views

app_name = "teachers"

urlpatterns = [
    path("", views.teacher_list, name="list"),
    path("<slug:slug>/", views.teacher_detail, name="detail"),
]
