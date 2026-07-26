"""
Doctor routes.
Handles doctor dashboard, patient history, prescriptions, and appointment status updates.
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.db import fetch_one, fetch_all, execute_query, execute_insert

doctor_bp = Blueprint("doctor", __name__, url_prefix="/doctor")


def doctor_required(f):
    """Decorator to restrict access to doctor users only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "doctor":
            flash("Access denied. Doctor privileges required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


@doctor_bp.route("/dashboard")
@doctor_required
def dashboard():
    """Display doctor dashboard with today's appointments and stats."""
    doctor_id = session["user_id"]

    today_appointments = fetch_all(
        """SELECT a.*, p.first_name, p.last_name, p.phone, p.gender
           FROM appointments a
           JOIN patients p ON a.patient_id = p.id
           WHERE a.doctor_id = %s AND a.appointment_date = CURDATE()
           ORDER BY a.appointment_time""",
        (doctor_id,),
    )

    stats = {
        "today_count": len(today_appointments),
        "total_patients": fetch_one(
            "SELECT COUNT(DISTINCT patient_id) as count FROM prescriptions WHERE doctor_id = %s",
            (doctor_id,),
        )["count"],
        "completed_today": fetch_one(
            """SELECT COUNT(*) as count FROM appointments
               WHERE doctor_id = %s AND appointment_date = CURDATE() AND status = 'Completed'""",
            (doctor_id,),
        )["count"],
        "pending_appointments": fetch_one(
            """SELECT COUNT(*) as count FROM appointments
               WHERE doctor_id = %s AND appointment_date >= CURDATE() AND status = 'Scheduled'""",
            (doctor_id,),
        )["count"],
    }

    return render_template(
        "dashboard_doctor.html",
        today_appointments=today_appointments,
        stats=stats,
    )


@doctor_bp.route("/patients")
@doctor_required
def patients():
    """View all patients who have had appointments with this doctor."""
    doctor_id = session["user_id"]
    patients_list = fetch_all(
        """SELECT DISTINCT p.*, d.full_name as doctor_name
           FROM patients p
           JOIN appointments a ON p.id = a.patient_id
           LEFT JOIN doctors d ON p.assigned_doctor_id = d.id
           WHERE a.doctor_id = %s
           ORDER BY p.id DESC""",
        (doctor_id,),
    )
    return render_template("patients.html", patients=patients_list, role="doctor", search="", page=1, total_pages=1)


@doctor_bp.route("/patient/<int:patient_id>")
@doctor_required
def patient_view(patient_id):
    """View patient details, prescriptions, and appointment history."""
    patient = fetch_one(
        """SELECT p.*, d.full_name as doctor_name FROM patients p
           LEFT JOIN doctors d ON p.assigned_doctor_id = d.id WHERE p.id = %s""",
        (patient_id,),
    )
    if not patient:
        flash("Patient not found.", "danger")
        return redirect(url_for("doctor.patients"))

    appointments = fetch_all(
        """SELECT a.*, d.full_name as doctor_name FROM appointments a
           JOIN doctors d ON a.doctor_id = d.id
           WHERE a.patient_id = %s ORDER BY a.appointment_date DESC""",
        (patient_id,),
    )
    prescriptions = fetch_all(
        """SELECT pr.*, d.full_name as doctor_name FROM prescriptions pr
           JOIN doctors d ON pr.doctor_id = d.id
           WHERE pr.patient_id = %s ORDER BY pr.prescribed_date DESC""",
        (patient_id,),
    )
    bills = fetch_all(
        "SELECT * FROM bills WHERE patient_id = %s ORDER BY bill_date DESC",
        (patient_id,),
    )
    return render_template(
        "patient_view.html",
        patient=patient,
        appointments=appointments,
        prescriptions=prescriptions,
        bills=bills,
    )


@doctor_bp.route("/appointment/<int:appointment_id>/status", methods=["POST"])
@doctor_required
def update_status(appointment_id):
    """Update appointment status (Completed or No-Show)."""
    status = request.form.get("status", "Completed")
    execute_query(
        "UPDATE appointments SET status = %s WHERE id = %s",
        (status, appointment_id),
    )
    flash(f"Appointment marked as {status}.", "success")
    return redirect(url_for("doctor.dashboard"))


@doctor_bp.route("/prescriptions/add/<int:appointment_id>", methods=["GET", "POST"])
@doctor_required
def add_prescription(appointment_id):
    """Add a prescription for a completed appointment."""
    doctor_id = session["user_id"]
    appointment = fetch_one(
        """SELECT a.*, p.first_name, p.last_name FROM appointments a
           JOIN patients p ON a.patient_id = p.id WHERE a.id = %s AND a.doctor_id = %s""",
        (appointment_id, doctor_id),
    )
    if not appointment:
        flash("Appointment not found.", "danger")
        return redirect(url_for("doctor.dashboard"))

    if request.method == "POST":
        diagnosis = request.form.get("diagnosis", "").strip()
        prescription_text = request.form.get("prescription_text", "").strip()
        medicine_details = request.form.get("medicine_details", "").strip()
        notes = request.form.get("notes", "").strip()

        if not diagnosis or not prescription_text:
            flash("Diagnosis and prescription are required.", "danger")
            return render_template("prescription_form.html", appointment=appointment, data=request.form)

        execute_insert(
            """INSERT INTO prescriptions (appointment_id, patient_id, doctor_id, diagnosis,
               prescription_text, medicine_details, notes)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                appointment_id, appointment["patient_id"], doctor_id,
                diagnosis, prescription_text, medicine_details, notes,
            ),
        )
        flash("Prescription added successfully.", "success")
        return redirect(url_for("doctor.dashboard"))

    return render_template("prescription_form.html", appointment=appointment, data={})


@doctor_bp.route("/prescriptions")
@doctor_required
def prescriptions():
    """View all prescriptions written by this doctor."""
    doctor_id = session["user_id"]
    prescriptions_list = fetch_all(
        """SELECT pr.*, p.first_name, p.last_name
           FROM prescriptions pr
           JOIN patients p ON pr.patient_id = p.id
           WHERE pr.doctor_id = %s
           ORDER BY pr.prescribed_date DESC""",
        (doctor_id,),
    )
    return render_template("prescriptions.html", prescriptions=prescriptions_list, role="doctor")
