from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from .models import Appointment, Patient


User = get_user_model()


class SignUpForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "you@example.com"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))
    password_confirmation = forms.CharField(label="Confirm password", widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(username=email).exists() or User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        if password and password != cleaned_data.get("password_confirmation"):
            self.add_error("password_confirmation", "Passwords do not match.")
        if password:
            validate_password(password)
        return cleaned_data

    def save(self):
        email = self.cleaned_data["email"]
        return User.objects.create_user(username=email, email=email, password=self.cleaned_data["password"])


class EmailLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "you@example.com"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))


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
