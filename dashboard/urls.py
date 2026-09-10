from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.public_home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("admin/login/", views.admin_login, name="admin_login"),
    path("admin/logout/", views.admin_logout, name="admin_logout"),
    path("admin/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/appointments/", views.appointments, name="appointments"),
    path("admin/patients/", views.patients, name="patients"),
]
