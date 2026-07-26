"""
Patient routes.
Handles patient registration, listing, editing, and viewing.
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.db import fetch_one, fetch_all, execute_query, execute_insert

patient_bp = Blueprint("patient", __name__, url_prefix="/patient")


def login_required(f):
    """Decorator to ensure user is logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "role" not in session:
            flash("Please log in first.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


@patient_bp.route("/")
@login_required
def list_patients():
    """List all patients with search and pagination."""
    search = request.args.get("search", "").strip()
    page = int(request.args.get("page", 1))
    per_page = 10
    offset = (page - 1) * per_page

    if search:
        patients_list = fetch_all(
            """SELECT p.*, d.full_name as doctor_name FROM patients p
               LEFT JOIN doctors d ON p.assigned_doctor_id = d.id
               WHERE p.first_name LIKE %s OR p.last_name LIKE %s OR p.phone LIKE %s
               ORDER BY p.id DESC LIMIT %s OFFSET %s""",
            (f"%{search}%", f"%{search}%", f"%{search}%", per_page, offset),
        )
        total = fetch_one(
            """SELECT COUNT(*) as count FROM patients
               WHERE first_name LIKE %s OR last_name LIKE %s OR phone LIKE %s""",
            (f"%{search}%", f"%{search}%", f"%{search}%"),
        )["count"]
    else:
        patients_list = fetch_all(
            """SELECT p.*, d.full_name as doctor_name FROM patients p
               LEFT JOIN doctors d ON p.assigned_doctor_id = d.id
               ORDER BY p.id DESC LIMIT %s OFFSET %s""",
            (per_page, offset),
        )
        total = fetch_one("SELECT COUNT(*) as count FROM patients")["count"]

    total_pages = (total + per_page - 1) // per_page
    return render_template(
        "patients.html",
        patients=patients_list,
        search=search,
        page=page,
        total_pages=total_pages,
        role=session.get("role"),
    )


@patient_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_patient():
    """Register a new patient."""
    if request.method == "POST":
        data = {
            "first_name": request.form.get("first_name", "").strip(),
            "last_name": request.form.get("last_name", "").strip(),
            "date_of_birth": request.form.get("date_of_birth", "").strip(),
            "gender": request.form.get("gender", ""),
            "email": request.form.get("email", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "address": request.form.get("address", "").strip(),
            "blood_group": request.form.get("blood_group", ""),
            "allergies": request.form.get("allergies", "").strip(),
            "medical_history": request.form.get("medical_history", "").strip(),
            "assigned_doctor_id": request.form.get("assigned_doctor_id") or None,
        }

        if not data["first_name"] or not data["last_name"] or not data["phone"] or not data["gender"] or not data["date_of_birth"]:
            flash("First name, last name, phone, gender, and date of birth are required.", "danger")
            doctors_list = fetch_all("SELECT id, full_name FROM doctors ORDER BY full_name")
            return render_template("patient_form.html", patient=None, data=data, doctors=doctors_list)

        execute_insert(
            """INSERT INTO patients (first_name, last_name, date_of_birth, gender, email,
               phone, address, blood_group, allergies, medical_history, assigned_doctor_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                data["first_name"], data["last_name"], data["date_of_birth"],
                data["gender"], data["email"], data["phone"], data["address"],
                data["blood_group"], data["allergies"], data["medical_history"],
                data["assigned_doctor_id"],
            ),
        )
        flash("Patient registered successfully.", "success")

        if session.get("role") == "receptionist":
            return redirect(url_for("receptionist.dashboard"))
        return redirect(url_for("patient.list_patients"))

    doctors_list = fetch_all("SELECT id, full_name FROM doctors ORDER BY full_name")
    return render_template("patient_form.html", patient=None, data={}, doctors=doctors_list)


@patient_bp.route("/edit/<int:patient_id>", methods=["GET", "POST"])
@login_required
def edit_patient(patient_id):
    """Edit patient details."""
    patient = fetch_one("SELECT * FROM patients WHERE id = %s", (patient_id,))
    if not patient:
        flash("Patient not found.", "danger")
        return redirect(url_for("patient.list_patients"))

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        date_of_birth = request.form.get("date_of_birth", "").strip()
        gender = request.form.get("gender", "")
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        blood_group = request.form.get("blood_group", "")
        allergies = request.form.get("allergies", "").strip()
        medical_history = request.form.get("medical_history", "").strip()
        assigned_doctor_id = request.form.get("assigned_doctor_id") or None

        if not first_name or not last_name or not phone:
            flash("First name, last name, and phone are required.", "danger")
            doctors_list = fetch_all("SELECT id, full_name FROM doctors ORDER BY full_name")
            return render_template("patient_form.html", patient=patient, data=request.form, doctors=doctors_list)

        execute_query(
            """UPDATE patients SET first_name=%s, last_name=%s, date_of_birth=%s, gender=%s,
               email=%s, phone=%s, address=%s, blood_group=%s, allergies=%s,
               medical_history=%s, assigned_doctor_id=%s WHERE id=%s""",
            (
                first_name, last_name, date_of_birth, gender, email, phone,
                address, blood_group, allergies, medical_history,
                assigned_doctor_id, patient_id,
            ),
        )
        flash("Patient details updated successfully.", "success")
        return redirect(url_for("patient.view_patient", patient_id=patient_id))

    doctors_list = fetch_all("SELECT id, full_name FROM doctors ORDER BY full_name")
    return render_template("patient_form.html", patient=patient, data=patient, doctors=doctors_list)


@patient_bp.route("/view/<int:patient_id>")
@login_required
def view_patient(patient_id):
    """View patient details with appointment and billing history."""
    patient = fetch_one(
        """SELECT p.*, d.full_name as doctor_name FROM patients p
           LEFT JOIN doctors d ON p.assigned_doctor_id = d.id WHERE p.id = %s""",
        (patient_id,),
    )
    if not patient:
        flash("Patient not found.", "danger")
        return redirect(url_for("patient.list_patients"))

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


@patient_bp.route("/delete/<int:patient_id>", methods=["POST"])
@login_required
def delete_patient(patient_id):
    """Delete a patient record."""
    execute_query("DELETE FROM patients WHERE id = %s", (patient_id,))
    flash("Patient deleted successfully.", "success")
    return redirect(url_for("patient.list_patients"))
