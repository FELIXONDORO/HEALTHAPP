# Apex Homecare dashboard

A small Django starter app for a healthcare services practice. It includes a responsive dashboard, today's appointments, patient overview, and working Patients and Appointments pages.

## Run locally

This project needs Python 3.11+ installed on Windows.

```powershell
cd C:\Users\USER\.vscode\projects\Healthapp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

If PowerShell blocks activation, run this once in an elevated PowerShell window or use the virtual environment directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

The dashboard currently uses representative in-memory data so it can be previewed immediately. The SQLite database and Django admin are configured for the next step of adding real patient, appointment, and authentication models.
