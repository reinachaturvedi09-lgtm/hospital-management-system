"""
Receptionist routes.
Handles receptionist dashboard and quick access to patient, appointment, and billing modules.
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.db import fetch_one, fetch_all

receptionist_bp = Blueprint("receptionist", __name__, url_prefix="/receptionist")


def receptionist_required(f):
    """Decorator to restrict access to receptionist users only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "receptionist":
            flash("Access denied. Receptionist privileges required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


@receptionist_bp.route("/dashboard")
@receptionist_required
def dashboard():
    """Display receptionist dashboard with statistics and quick actions."""
    stats = {
        "today_appointments": fetch_one(
            "SELECT COUNT(*) as count FROM appointments WHERE appointment_date = CURDATE()"
        )["count"],
        "total_patients": fetch_one("SELECT COUNT(*) as count FROM patients")["count"],
        "pending_bills": fetch_one(
            "SELECT COUNT(*) as count FROM bills WHERE payment_status != 'Paid'"
        )["count"],
        "scheduled_appointments": fetch_one(
            """SELECT COUNT(*) as count FROM appointments
               WHERE appointment_date >= CURDATE() AND status = 'Scheduled'"""
        )["count"],
    }

    recent_patients = fetch_all(
        "SELECT * FROM patients ORDER BY registration_date DESC LIMIT 5"
    )
    today_appointments = fetch_all(
        """SELECT a.*, p.first_name, p.last_name, d.full_name as doctor_name
           FROM appointments a
           JOIN patients p ON a.patient_id = p.id
           JOIN doctors d ON a.doctor_id = d.id
           WHERE a.appointment_date = CURDATE()
           ORDER BY a.appointment_time"""
    )

    return render_template(
        "dashboard_receptionist.html",
        stats=stats,
        recent_patients=recent_patients,
        today_appointments=today_appointments,
    )
