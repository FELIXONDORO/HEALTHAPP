import os
import secrets
from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login as auth_login, logout as auth_logout
from django.db.models import Count
from django.shortcuts import redirect, render

from .forms import AppointmentForm, EmailLoginForm, PatientForm, SignUpForm
from .models import Appointment, Patient


APPOINTMENTS = [
    {"time": "09:00 AM", "patient": "Maya Thompson", "type": "Annual check-up", "status": "Confirmed", "initials": "MT", "tone": "lavender"},
    {"time": "10:30 AM", "patient": "Ethan Williams", "type": "Follow-up consultation", "status": "Confirmed", "initials": "EW", "tone": "mint"},
    {"time": "01:15 PM", "patient": "Olivia Martinez", "type": "Nutrition consultation", "status": "Pending", "initials": "OM", "tone": "peach"},
    {"time": "03:00 PM", "patient": "Noah Johnson", "type": "Lab results review", "status": "Confirmed", "initials": "NJ", "tone": "blue"},
]

PATIENTS = [
    {"name": "Maya Thompson", "email": "maya.t@example.com", "last_visit": "Today, 09:00 AM", "status": "Active", "initials": "MT", "tone": "lavender"},
    {"name": "Ethan Williams", "email": "ethan.w@example.com", "last_visit": "Today, 10:30 AM", "status": "Active", "initials": "EW", "tone": "mint"},
    {"name": "Olivia Martinez", "email": "olivia.m@example.com", "last_visit": "Yesterday, 02:00 PM", "status": "Follow-up", "initials": "OM", "tone": "peach"},
    {"name": "Noah Johnson", "email": "noah.j@example.com", "last_visit": "May 26, 2024", "status": "Active", "initials": "NJ", "tone": "blue"},
]

User = get_user_model()


def allowed_admin_emails():
    return {email.strip().lower() for email in os.environ.get("ADMIN_EMAIL", "").split(",") if email.strip()}


def admin_required(view):
    @wraps(view)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.session.get("apex_admin_authenticated"):
            return redirect("dashboard:admin_login")
        return view(request, *args, **kwargs)

    return wrapped_view


def public_home(request):
    return render(request, "dashboard/public_home.html", {"services": [("heart-pulse", "Medical check-ups", "Blood pressure, blood sugar, SpO2 and temperature checks in the comfort of home."), ("cross", "Nursing care", "Compassionate wound care, catheter care and post-hospital recovery support."), ("accessibility", "Physiotherapy", "Coordinated physiotherapy services that help you regain confidence and mobility."), ("apple", "Nutrition support", "Nutritional consultation and practical weight-management guidance."), ("hand-heart", "Elderly care", "Thoughtful elderly visits, reports and chronic disease management."), ("baby", "Mother & baby care", "Antenatal, postnatal and family health support when you need it most.")]})


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        auth_login(request, user)
        if user.email.lower() in allowed_admin_emails():
            messages.success(request, "Your account is ready. Use the administrator password to access the dashboard.")
            return redirect("dashboard:admin_login")
        messages.success(request, "Your account has been created successfully.")
        return redirect("dashboard:home")
    return render(
        request,
        "dashboard/auth_form.html",
        {
            "form": form,
            "page_title": "Create your account",
            "page_subtitle": "Start your journey with personalized home healthcare.",
            "auth_mode": "signup",
            "google_button_label": "Sign up with Google",
            "divider_label": "or register with email",
            "submit_label": "Create Account",
            "alternate_prompt": "Already have an account?",
            "alternate_url": "dashboard:login",
            "alternate_text": "Sign in",
        },
    )


def login(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    form = EmailLoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"].lower()
        user = authenticate(request, username=email, password=form.cleaned_data["password"])
        if user is not None:
            auth_login(request, user)
            messages.success(request, "Welcome back.")
            return redirect("dashboard:home")
        form.add_error(None, "Incorrect email or password.")
    return render(
        request,
        "dashboard/auth_form.html",
        {
            "form": form,
            "page_title": "Welcome back",
            "page_subtitle": "Sign in to your Apex Homecare account.",
            "auth_mode": "login",
            "google_button_label": "Sign in with Google",
            "divider_label": "or sign in with email",
            "submit_label": "Sign In",
            "alternate_prompt": "Don't have an account?",
            "alternate_url": "dashboard:signup",
            "alternate_text": "Create an account",
        },
    )


def logout(request):
    request.session.pop("apex_admin_authenticated", None)
    auth_logout(request)
    return redirect("dashboard:home")


def admin_login(request):
    if request.user.is_authenticated and request.session.get("apex_admin_authenticated"):
        return redirect("dashboard:admin_dashboard")
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        expected_password = os.environ.get("ADMIN_PASSWORD", "")
        user = User.objects.filter(email__iexact=email).first()
        if user and email in allowed_admin_emails() and expected_password and secrets.compare_digest(password, expected_password):
            auth_login(request, user)
            request.session["apex_admin_authenticated"] = True
            return redirect("dashboard:admin_dashboard")
        messages.error(request, "Use a registered, authorised administrator email and the administrator password.")
    return render(request, "dashboard/admin_login.html")


def admin_logout(request):
    return logout(request)


@admin_required
def admin_dashboard(request):
    context = {
        "active_page": "dashboard",
        "appointments": APPOINTMENTS,
        "patients": PATIENTS,
        "chart_heights": [35, 50, 44, 62, 54, 76, 68, 84, 72, 92, 80, 100],
        "stats": [
            {"label": "Total patients", "value": "1,284", "change": "+12.5%", "icon": "users", "trend": "up"},
            {"label": "Appointments", "value": "248", "change": "+8.2%", "icon": "calendar", "trend": "up"},
            {"label": "New messages", "value": "36", "change": "-3.1%", "icon": "message", "trend": "down"},
            {"label": "Satisfaction rate", "value": "96.8%", "change": "+2.4%", "icon": "heart", "trend": "up"},
        ],
    }
    return render(request, "dashboard/dashboard.html", context)


@admin_required
def appointments(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save()
            messages.success(request, f"Appointment for {appointment.patient} was created.")
            return redirect("dashboard:appointments")
    else:
        form = AppointmentForm()

    return render(
        request,
        "dashboard/list.html",
        {
            "active_page": "appointments",
            "page_title": "Appointments",
            "page_subtitle": "Keep track of upcoming patient visits.",
            "items": Appointment.objects.select_related("patient").order_by("starts_at"),
            "item_type": "appointment",
            "form": form,
        },
    )


@admin_required
def patients(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            messages.success(request, f"{patient.name} was added. You can now select them when scheduling an appointment.")
            return redirect("dashboard:patients")
    else:
        form = PatientForm()

    return render(
        request,
        "dashboard/list.html",
        {
            "active_page": "patients",
            "page_title": "Patients",
            "page_subtitle": "Manage your patient relationships in one place.",
            "items": Patient.objects.annotate(appointment_count=Count("appointments")).order_by("name"),
            "item_type": "patient",
            "form": form,
        },
    )
