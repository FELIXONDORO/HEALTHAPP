from django.contrib import messages
from django.db.models import Count
from django.shortcuts import redirect, render

from .forms import AppointmentForm, PatientForm
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


def dashboard(request):
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
