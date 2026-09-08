from django.db import models


class Patient(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    starts_at = models.DateTimeField()
    visit_type = models.CharField(max_length=120)
    status = models.CharField(max_length=30, default="Pending")

    def __str__(self):
        return f"{self.patient} - {self.starts_at:%Y-%m-%d %H:%M}"
