"""
Billing routes.
Handles bill generation, listing, editing, and invoice printing.
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.db import fetch_one, fetch_all, execute_query, execute_insert

billing_bp = Blueprint("billing", __name__, url_prefix="/billing")


def login_required(f):
    """Decorator to ensure user is logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "role" not in session:
            flash("Please log in first.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


@billing_bp.route("/")
@login_required
def list_bills():
    """List all billing records with search and filters."""
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


@billing_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_bill():
    """Generate a new bill for a patient."""
    if request.method == "POST":
        patient_id = request.form.get("patient_id", type=int)
        appointment_id = request.form.get("appointment_id") or None
        consultation_fee = request.form.get("consultation_fee", 0, type=float)
        medicine_charges = request.form.get("medicine_charges", 0, type=float)
        lab_charges = request.form.get("lab_charges", 0, type=float)
        other_charges = request.form.get("other_charges", 0, type=float)
        payment_status = request.form.get("payment_status", "Unpaid")
        payment_method = request.form.get("payment_method", "Cash")

        total_amount = consultation_fee + medicine_charges + lab_charges + other_charges

        if not patient_id:
            flash("Patient is required.", "danger")
            patients_list = fetch_all("SELECT id, first_name, last_name FROM patients ORDER BY first_name")
            appointments_list = fetch_all(
                """SELECT id, CONCAT(first_name, ' - ', DATE_FORMAT(appointment_date, '%%Y-%%m-%%d')) as label
                   FROM (SELECT a.id, p.first_name, a.appointment_date
                         FROM appointments a JOIN patients p ON a.patient_id = p.id) sub
                   ORDER BY appointment_date DESC"""
            )
            return render_template(
                "bill_form.html",
                patients=patients_list,
                appointments=appointments_list,
                data=request.form,
                bill=None,
            )

        execute_insert(
            """INSERT INTO bills (patient_id, appointment_id, consultation_fee,
               medicine_charges, lab_charges, other_charges, total_amount,
               payment_status, payment_method)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                patient_id, appointment_id, consultation_fee, medicine_charges,
                lab_charges, other_charges, total_amount, payment_status, payment_method,
            ),
        )
        flash("Bill generated successfully.", "success")

        if session.get("role") == "receptionist":
            return redirect(url_for("receptionist.dashboard"))
        return redirect(url_for("billing.list_bills"))

    patients_list = fetch_all("SELECT id, first_name, last_name FROM patients ORDER BY first_name")
    appointments_list = fetch_all(
        """SELECT a.id, CONCAT(p.first_name, ' - ', a.appointment_date) as label
           FROM appointments a
           JOIN patients p ON a.patient_id = p.id
           ORDER BY a.appointment_date DESC"""
    )
    return render_template(
        "bill_form.html",
        patients=patients_list,
        appointments=appointments_list,
        data={},
        bill=None,
    )


@billing_bp.route("/edit/<int:bill_id>", methods=["GET", "POST"])
@login_required
def edit_bill(bill_id):
    """Edit an existing bill."""
    bill = fetch_one("SELECT * FROM bills WHERE id = %s", (bill_id,))
    if not bill:
        flash("Bill not found.", "danger")
        return redirect(url_for("billing.list_bills"))

    if request.method == "POST":
        consultation_fee = request.form.get("consultation_fee", 0, type=float)
        medicine_charges = request.form.get("medicine_charges", 0, type=float)
        lab_charges = request.form.get("lab_charges", 0, type=float)
        other_charges = request.form.get("other_charges", 0, type=float)
        payment_status = request.form.get("payment_status", "Unpaid")
        payment_method = request.form.get("payment_method", "Cash")

        total_amount = consultation_fee + medicine_charges + lab_charges + other_charges

        execute_query(
            """UPDATE bills SET consultation_fee=%s, medicine_charges=%s, lab_charges=%s,
               other_charges=%s, total_amount=%s, payment_status=%s, payment_method=%s
               WHERE id=%s""",
            (
                consultation_fee, medicine_charges, lab_charges, other_charges,
                total_amount, payment_status, payment_method, bill_id,
            ),
        )
        flash("Bill updated successfully.", "success")
        return redirect(url_for("billing.list_bills"))

    patients_list = fetch_all("SELECT id, first_name, last_name FROM patients ORDER BY first_name")
    appointments_list = fetch_all(
        """SELECT a.id, CONCAT(p.first_name, ' - ', a.appointment_date) as label
           FROM appointments a
           JOIN patients p ON a.patient_id = p.id
           ORDER BY a.appointment_date DESC"""
    )
    return render_template(
        "bill_form.html",
        patients=patients_list,
        appointments=appointments_list,
        data=bill,
        bill=bill,
    )


@billing_bp.route("/print/<int:bill_id>")
@login_required
def print_bill(bill_id):
    """Print invoice for a bill."""
    bill = fetch_one(
        """SELECT b.*, p.first_name, p.last_name, p.phone, p.address, p.gender, p.date_of_birth
           FROM bills b
           JOIN patients p ON b.patient_id = p.id
           WHERE b.id = %s""",
        (bill_id,),
    )
    if not bill:
        flash("Bill not found.", "danger")
        return redirect(url_for("billing.list_bills"))

    appointment_info = None
    if bill.get("appointment_id"):
        appointment_info = fetch_one(
            """SELECT a.*, d.full_name as doctor_name FROM appointments a
               JOIN doctors d ON a.doctor_id = d.id WHERE a.id = %s""",
            (bill["appointment_id"],),
        )

    return render_template("bill_print.html", bill=bill, appointment=appointment_info)
