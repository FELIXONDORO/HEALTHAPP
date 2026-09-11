import re
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from .models import Appointment, Patient


User = get_user_model()


class SignUpForm(forms.Form):
    email = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "you@example.com", "autofocus": True}),
    )
    password = forms.CharField(
        label="Password",
        help_text="Must be at least 8 characters with uppercase, lowercase, a number, and a special character.",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "placeholder": "••••••••"}),
    )
    password_confirmation = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "placeholder": "••••••••"}),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(username=email).exists() or User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not password:
            return password

        errors = []
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter (A-Z).")
        if not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter (a-z).")
        if not re.search(r"[0-9]", password):
            errors.append("Password must contain at least one number (0-9).")
        
        special_chars = set("!@#$%^&*()_+-=[]{};':\",./<>?~`|\\")
        if not any(char in special_chars for char in password):
            errors.append("Password must contain at least one special character (e.g. !@#$%^&*).")

        try:
            validate_password(password)
        except forms.ValidationError as e:
            errors.extend(e.messages)

        if errors:
            raise forms.ValidationError(errors)

        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")
        if password and password_confirmation and password != password_confirmation:
            self.add_error("password_confirmation", "Passwords do not match.")
        return cleaned_data

    def save(self):
        email = self.cleaned_data["email"]
        return User.objects.create_user(username=email, email=email, password=self.cleaned_data["password"])


class EmailLoginForm(forms.Form):
    email = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "you@example.com", "autofocus": True}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password", "placeholder": "••••••••"}),
    )


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["name", "email"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Maya Thompson", "autofocus": True}),
            "email": forms.EmailInput(attrs={"placeholder": "maya@example.com"}),
        }


class AppointmentForm(forms.ModelForm):
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.order_by("name"),
        required=False,
        empty_label="Select an existing patient",
    )
    patient_name = forms.CharField(
        required=False,
        max_length=120,
        label="Or new patient name",
        widget=forms.TextInput(attrs={"placeholder": "e.g. Maya Thompson"}),
    )
    patient_email = forms.EmailField(
        required=False,
        label="New patient email",
        widget=forms.EmailInput(attrs={"placeholder": "maya@example.com"}),
    )
    starts_at = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
    )

    class Meta:
        model = Appointment
        fields = ["patient", "starts_at", "visit_type", "status"]
        widgets = {
            "visit_type": forms.TextInput(attrs={"placeholder": "e.g. Annual check-up"}),
            "status": forms.Select(choices=[("Pending", "Pending"), ("Confirmed", "Confirmed"), ("Cancelled", "Cancelled")]),
        }

    def clean(self):
        cleaned_data = super().clean()
        patient = cleaned_data.get("patient")
        name = cleaned_data.get("patient_name")
        email = cleaned_data.get("patient_email")

        if not patient and not (name and email):
            raise forms.ValidationError("Select an existing patient or provide a new patient's name and email.")
        if (name and not email) or (email and not name):
            raise forms.ValidationError("Provide both a name and email when adding a new patient.")
        return cleaned_data

    def save(self, commit=True):
        appointment = super().save(commit=False)
        if not self.cleaned_data["patient"]:
            patient, _ = Patient.objects.get_or_create(
                email=self.cleaned_data["patient_email"],
                defaults={"name": self.cleaned_data["patient_name"]},
            )
            appointment.patient = patient
        if commit:
            appointment.save()
        return appointment
