"""
Appointment routes.
Handles booking, cancelling, rescheduling, and searching appointments.
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.db import fetch_one, fetch_all, execute_query, execute_insert

appointment_bp = Blueprint("appointment", __name__, url_prefix="/appointment")


def login_required(f):
    """Decorator to ensure user is logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "role" not in session:
            flash("Please log in first.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


@appointment_bp.route("/")
@login_required
def list_appointments():
    """List all appointments with search and filters."""
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()
    date = request.args.get("date", "").strip()
    page = int(request.args.get("page", 1))
    per_page = 10
    offset = (page - 1) * per_page

    query = """SELECT a.*, p.first_name, p.last_name, d.full_name as doctor_name
               FROM appointments a
               JOIN patients p ON a.patient_id = p.id
               JOIN doctors d ON a.doctor_id = d.id WHERE 1=1"""
    params = []

    if search:
        query += " AND (p.first_name LIKE %s OR p.last_name LIKE %s OR d.full_name LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if status:
        query += " AND a.status = %s"
        params.append(status)
    if date:
        query += " AND a.appointment_date = %s"
        params.append(date)

    count_query = query.replace(
        "SELECT a.*, p.first_name, p.last_name, d.full_name as doctor_name",
        "SELECT COUNT(*) as count",
    )
    total = fetch_one(count_query, params)["count"]

    query += " ORDER BY a.appointment_date DESC, a.appointment_time DESC LIMIT %s OFFSET %s"
    params.extend([per_page, offset])
    appointments_list = fetch_all(query, params)

    total_pages = (total + per_page - 1) // per_page
    return render_template(
        "appointments.html",
        appointments=appointments_list,
        search=search,
        status=status,
        date=date,
        page=page,
        total_pages=total_pages,
        role=session.get("role"),
    )


@appointment_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_appointment():
    """Book a new appointment."""
    if request.method == "POST":
        patient_id = request.form.get("patient_id", type=int)
        doctor_id = request.form.get("doctor_id", type=int)
        appointment_date = request.form.get("appointment_date", "").strip()
        appointment_time = request.form.get("appointment_time", "").strip()
        reason = request.form.get("reason", "").strip()

        if not patient_id or not doctor_id or not appointment_date or not appointment_time:
            flash("Patient, doctor, date, and time are required.", "danger")
            patients_list = fetch_all("SELECT id, first_name, last_name FROM patients ORDER BY first_name")
            doctors_list = fetch_all("SELECT id, full_name FROM doctors WHERE availability = 'Available' ORDER BY full_name")
            return render_template(
                "appointment_form.html",
                patients=patients_list,
                doctors=doctors_list,
                data=request.form,
                appointment=None,
            )

        conflict = fetch_one(
            """SELECT id FROM appointments
               WHERE doctor_id = %s AND appointment_date = %s AND appointment_time = %s
               AND status = 'Scheduled'""",
            (doctor_id, appointment_date, appointment_time),
        )
        if conflict:
            flash("This time slot is already booked for the selected doctor.", "danger")
            patients_list = fetch_all("SELECT id, first_name, last_name FROM patients ORDER BY first_name")
            doctors_list = fetch_all("SELECT id, full_name FROM doctors WHERE availability = 'Available' ORDER BY full_name")
            return render_template(
                "appointment_form.html",
                patients=patients_list,
                doctors=doctors_list,
                data=request.form,
                appointment=None,
            )

        execute_insert(
            """INSERT INTO appointments (patient_id, doctor_id, appointment_date,
               appointment_time, reason, created_by)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (patient_id, doctor_id, appointment_date, appointment_time, reason, session.get("user_id")),
        )
        flash("Appointment booked successfully.", "success")

        if session.get("role") == "receptionist":
            return redirect(url_for("receptionist.dashboard"))
        return redirect(url_for("appointment.list_appointments"))

    patients_list = fetch_all("SELECT id, first_name, last_name FROM patients ORDER BY first_name")
    doctors_list = fetch_all(
        "SELECT id, full_name FROM doctors WHERE availability = 'Available' ORDER BY full_name"
    )
    return render_template(
        "appointment_form.html",
        patients=patients_list,
        doctors=doctors_list,
        data={},
        appointment=None,
    )


@appointment_bp.route("/edit/<int:appointment_id>", methods=["GET", "POST"])
@login_required
def edit_appointment(appointment_id):
    """Reschedule an existing appointment."""
    appointment = fetch_one("SELECT * FROM appointments WHERE id = %s", (appointment_id,))
    if not appointment:
        flash("Appointment not found.", "danger")
        return redirect(url_for("appointment.list_appointments"))

    if request.method == "POST":
        doctor_id = request.form.get("doctor_id", type=int)
        appointment_date = request.form.get("appointment_date", "").strip()
        appointment_time = request.form.get("appointment_time", "").strip()
        reason = request.form.get("reason", "").strip()
        status = request.form.get("status", "Scheduled")

        if not doctor_id or not appointment_date or not appointment_time:
            flash("Doctor, date, and time are required.", "danger")
            patients_list = fetch_all("SELECT id, first_name, last_name FROM patients ORDER BY first_name")
            doctors_list = fetch_all("SELECT id, full_name FROM doctors ORDER BY full_name")
            return render_template(
                "appointment_form.html",
                patients=patients_list,
                doctors=doctors_list,
                data=request.form,
                appointment=appointment,
            )

        execute_query(
            """UPDATE appointments SET doctor_id=%s, appointment_date=%s,
               appointment_time=%s, reason=%s, status=%s WHERE id=%s""",
            (doctor_id, appointment_date, appointment_time, reason, status, appointment_id),
        )
        flash("Appointment updated successfully.", "success")
        return redirect(url_for("appointment.list_appointments"))

    patients_list = fetch_all("SELECT id, first_name, last_name FROM patients ORDER BY first_name")
    doctors_list = fetch_all("SELECT id, full_name FROM doctors ORDER BY full_name")
    return render_template(
        "appointment_form.html",
        patients=patients_list,
        doctors=doctors_list,
        data=appointment,
        appointment=appointment,
    )


@appointment_bp.route("/cancel/<int:appointment_id>", methods=["POST"])
@login_required
def cancel_appointment(appointment_id):
    """Cancel an appointment."""
    execute_query(
        "UPDATE appointments SET status = 'Cancelled' WHERE id = %s",
        (appointment_id,),
    )
    flash("Appointment cancelled successfully.", "success")

    if session.get("role") == "receptionist":
        return redirect(url_for("receptionist.dashboard"))
    return redirect(url_for("appointment.list_appointments"))
