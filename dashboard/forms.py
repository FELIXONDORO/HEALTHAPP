from django import forms

from .models import Appointment, Patient


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
