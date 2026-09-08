from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard, name="home"),
    path("appointments/", views.appointments, name="appointments"),
    path("patients/", views.patients, name="patients"),
]
