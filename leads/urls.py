from django.urls import path

from . import views

app_name = "leads"

urlpatterns = [
    path("", views.enquiry, name="enquiry"),
    path("submit/", views.submit, name="submit"),
    path("thank-you/", views.thanks, name="thanks"),
]
