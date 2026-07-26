"""
Admin routes.
Handles admin dashboard, doctor management, and receptionist management.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.db import fetch_one, fetch_all, execute_query, execute_insert

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    """Decorator to restrict access to admin users only."""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Access denied. Admin privileges required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    """Display admin dashboard with statistics."""
    stats = {
        "total_doctors": fetch_one("SELECT COUNT(*) as count FROM doctors")["count"],
        "total_receptionists": fetch_one("SELECT COUNT(*) as count FROM receptionists")["count"],
        "total_patients": fetch_one("SELECT COUNT(*) as count FROM patients")["count"],
        "today_appointments": fetch_one(
            "SELECT COUNT(*) as count FROM appointments WHERE appointment_date = CURDATE()"
        )["count"],
        "total_appointments": fetch_one("SELECT COUNT(*) as count FROM appointments")["count"],
        "total_bills": fetch_one(
            "SELECT COALESCE(SUM(total_amount), 0) as total FROM bills"
        )["total"],
        "pending_bills": fetch_one(
            "SELECT COUNT(*) as count FROM bills WHERE payment_status != 'Paid'"
        )["count"],
    }
    recent_appointments = fetch_all(
        """SELECT a.*, p.first_name, p.last_name, d.full_name as doctor_name
           FROM appointments a
           JOIN patients p ON a.patient_id = p.id
           JOIN doctors d ON a.doctor_id = d.id
           ORDER BY a.created_at DESC LIMIT 5"""
    )
    return render_template(
        "dashboard_admin.html", stats=stats, recent_appointments=recent_appointments
    )


# ===================== Doctor Management =====================

@admin_bp.route("/doctors")
@admin_required
def doctors():
    """List all doctors with optional search."""
    search = request.args.get("search", "").strip()
    page = int(request.args.get("page", 1))
    per_page = 10
    offset = (page - 1) * per_page

    if search:
        doctors_list = fetch_all(
            """SELECT * FROM doctors
               WHERE full_name LIKE %s OR specialization LIKE %s OR email LIKE %s
               ORDER BY id DESC LIMIT %s OFFSET %s""",
            (f"%{search}%", f"%{search}%", f"%{search}%", per_page, offset),
        )
        total = fetch_one(
            """SELECT COUNT(*) as count FROM doctors
               WHERE full_name LIKE %s OR specialization LIKE %s OR email LIKE %s""",
            (f"%{search}%", f"%{search}%", f"%{search}%"),
        )["count"]
    else:
        doctors_list = fetch_all(
            "SELECT * FROM doctors ORDER BY id DESC LIMIT %s OFFSET %s",
            (per_page, offset),
        )
        total = fetch_one("SELECT COUNT(*) as count FROM doctors")["count"]

    total_pages = (total + per_page - 1) // per_page
    return render_template(
        "doctors.html",
        doctors=doctors_list,
        search=search,
        page=page,
        total_pages=total_pages,
    )


@admin_bp.route("/doctors/add", methods=["GET", "POST"])
@admin_required
def add_doctor():
    """Add a new doctor."""
    if request.method == "POST":
        data = {
            "username": request.form.get("username", "").strip(),
            "password": request.form.get("password", "").strip(),
            "full_name": request.form.get("full_name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "specialization": request.form.get("specialization", "").strip(),
            "qualification": request.form.get("qualification", "").strip(),
            "experience_years": request.form.get("experience_years", 0, type=int),
            "consultation_fee": request.form.get("consultation_fee", 500, type=float),
        }

        if not data["username"] or not data["password"] or not data["full_name"] or not data["specialization"]:
            flash("Username, password, full name, and specialization are required.", "danger")
            return render_template("doctor_form.html", doctor=None, data=data)

        existing = fetch_one("SELECT id FROM doctors WHERE username = %s", (data["username"],))
        if existing:
            flash("Username already exists.", "danger")
            return render_template("doctor_form.html", doctor=None, data=data)

        execute_insert(
            """INSERT INTO doctors (username, password, full_name, email, phone,
               specialization, qualification, experience_years, consultation_fee)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                data["username"], data["password"], data["full_name"], data["email"],
                data["phone"], data["specialization"], data["qualification"],
                data["experience_years"], data["consultation_fee"],
            ),
        )
        flash("Doctor added successfully.", "success")
        return redirect(url_for("admin.doctors"))

    return render_template("doctor_form.html", doctor=None, data={})


@admin_bp.route("/doctors/edit/<int:doctor_id>", methods=["GET", "POST"])
@admin_required
def edit_doctor(doctor_id):
    """Edit an existing doctor's details."""
    doctor = fetch_one("SELECT * FROM doctors WHERE id = %s", (doctor_id,))
    if not doctor:
        flash("Doctor not found.", "danger")
        return redirect(url_for("admin.doctors"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        specialization = request.form.get("specialization", "").strip()
        qualification = request.form.get("qualification", "").strip()
        experience_years = request.form.get("experience_years", 0, type=int)
        consultation_fee = request.form.get("consultation_fee", 500, type=float)
        availability = request.form.get("availability", "Available")

        if not full_name or not specialization:
            flash("Full name and specialization are required.", "danger")
            return render_template("doctor_form.html", doctor=doctor, data=request.form)

        execute_query(
            """UPDATE doctors SET full_name=%s, email=%s, phone=%s, specialization=%s,
               qualification=%s, experience_years=%s, consultation_fee=%s, availability=%s
               WHERE id=%s""",
            (
                full_name, email, phone, specialization, qualification,
                experience_years, consultation_fee, availability, doctor_id,
            ),
        )
        flash("Doctor updated successfully.", "success")
        return redirect(url_for("admin.doctors"))

    return render_template("doctor_form.html", doctor=doctor, data=doctor)


@admin_bp.route("/doctors/delete/<int:doctor_id>", methods=["POST"])
@admin_required
def delete_doctor(doctor_id):
    """Delete a doctor record."""
    execute_query("DELETE FROM doctors WHERE id = %s", (doctor_id,))
    flash("Doctor deleted successfully.", "success")
    return redirect(url_for("admin.doctors"))


# ===================== Receptionist Management =====================

@admin_bp.route("/receptionists")
@admin_required
def receptionists():
    """List all receptionists with optional search."""
    search = request.args.get("search", "").strip()
    page = int(request.args.get("page", 1))
    per_page = 10
    offset = (page - 1) * per_page

    if search:
        rec_list = fetch_all(
            """SELECT * FROM receptionists
               WHERE full_name LIKE %s OR email LIKE %s OR phone LIKE %s
               ORDER BY id DESC LIMIT %s OFFSET %s""",
            (f"%{search}%", f"%{search}%", f"%{search}%", per_page, offset),
        )
        total = fetch_one(
            """SELECT COUNT(*) as count FROM receptionists
               WHERE full_name LIKE %s OR email LIKE %s OR phone LIKE %s""",
            (f"%{search}%", f"%{search}%", f"%{search}%"),
        )["count"]
    else:
        rec_list = fetch_all(
            "SELECT * FROM receptionists ORDER BY id DESC LIMIT %s OFFSET %s",
            (per_page, offset),
        )
        total = fetch_one("SELECT COUNT(*) as count FROM receptionists")["count"]

    total_pages = (total + per_page - 1) // per_page
    return render_template(
        "receptionists.html",
        receptionists=rec_list,
        search=search,
        page=page,
        total_pages=total_pages,
    )


@admin_bp.route("/receptionists/add", methods=["GET", "POST"])
@admin_required
def add_receptionist():
    """Add a new receptionist."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        shift = request.form.get("shift", "Morning")

        if not username or not password or not full_name:
            flash("Username, password, and full name are required.", "danger")
            return render_template("receptionist_form.html", receptionist=None, data=request.form)

        existing = fetch_one("SELECT id FROM receptionists WHERE username = %s", (username,))
        if existing:
            flash("Username already exists.", "danger")
            return render_template("receptionist_form.html", receptionist=None, data=request.form)

        execute_insert(
            """INSERT INTO receptionists (username, password, full_name, email, phone, shift)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (username, password, full_name, email, phone, shift),
        )
        flash("Receptionist added successfully.", "success")
        return redirect(url_for("admin.receptionists"))

    return render_template("receptionist_form.html", receptionist=None, data={})


@admin_bp.route("/receptionists/edit/<int:rec_id>", methods=["GET", "POST"])
@admin_required
def edit_receptionist(rec_id):
    """Edit an existing receptionist's details."""
    rec = fetch_one("SELECT * FROM receptionists WHERE id = %s", (rec_id,))
    if not rec:
        flash("Receptionist not found.", "danger")
        return redirect(url_for("admin.receptionists"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        shift = request.form.get("shift", "Morning")

        if not full_name:
            flash("Full name is required.", "danger")
            return render_template("receptionist_form.html", receptionist=rec, data=request.form)

        execute_query(
            """UPDATE receptionists SET full_name=%s, email=%s, phone=%s, shift=%s WHERE id=%s""",
            (full_name, email, phone, shift, rec_id),
        )
        flash("Receptionist updated successfully.", "success")
        return redirect(url_for("admin.receptionists"))

    return render_template("receptionist_form.html", receptionist=rec, data=rec)


@admin_bp.route("/receptionists/delete/<int:rec_id>", methods=["POST"])
@admin_required
def delete_receptionist(rec_id):
    """Delete a receptionist record."""
    execute_query("DELETE FROM receptionists WHERE id = %s", (rec_id,))
    flash("Receptionist deleted successfully.", "success")
    return redirect(url_for("admin.receptionists"))


# ===================== View All Records =====================

@admin_bp.route("/patients")
@admin_required
def patients():
    """View all patients."""
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


@admin_bp.route("/appointments")
@admin_required
def appointments():
    """View all appointments."""
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


@admin_bp.route("/bills")
@admin_required
def bills():
    """View all billing records."""
    search = request.args.get("search", "").strip()
    payment_status = request.args.get("payment_status", "").strip()
    page = int(request.args.get("page", 1))
    per_page = 10
    offset = (page - 1) * per_page

    query = """SELECT b.*, p.first_name, p.last_name
               FROM bills b
               JOIN patients p ON b.patient_id = p.id WHERE 1=1"""
    params = []

    if search:
        query += " AND (p.first_name LIKE %s OR p.last_name LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])
    if payment_status:
        query += " AND b.payment_status = %s"
        params.append(payment_status)

    count_query = query.replace(
        "SELECT b.*, p.first_name, p.last_name",
        "SELECT COUNT(*) as count",
    )
    total = fetch_one(count_query, params)["count"]

    query += " ORDER BY b.bill_date DESC LIMIT %s OFFSET %s"
    params.extend([per_page, offset])
    bills_list = fetch_all(query, params)

    total_pages = (total + per_page - 1) // per_page
    return render_template(
        "bills.html",
        bills=bills_list,
        search=search,
        payment_status=payment_status,
        page=page,
        total_pages=total_pages,
        role=session.get("role"),
    )
