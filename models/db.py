"""
Database connection and query helper module.
Supports MySQL when configured, falls back to SQLite automatically.
"""

import os
import sqlite3
import pymysql
from config import Config

USE_SQLITE = not os.environ.get("DB_HOST")


def _get_db_path():
    """Return the SQLite database file path."""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "hospital.db")


def get_connection():
    """Create and return a database connection (MySQL or SQLite)."""
    if USE_SQLITE:
        db_path = _get_db_path()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    return pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        port=Config.DB_PORT,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def _convert_params(query, params):
    """Convert MySQL %s placeholders to SQLite ? placeholders."""
    if USE_SQLITE and params:
        query = query.replace("%s", "?")
    return query, params


def _rows_to_dicts(rows):
    """Convert sqlite3.Row objects to plain dicts."""
    if rows is None:
        return None
    if isinstance(rows, sqlite3.Row):
        return dict(rows)
    if isinstance(rows, list):
        return [dict(r) if isinstance(r, sqlite3.Row) else r for r in rows]
    return rows


def fetch_one(query, params=None):
    """Execute a query and return a single row as a dictionary."""
    query, params = _convert_params(query, params)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        result = cursor.fetchone()
        return _rows_to_dicts(result)
    finally:
        conn.close()


def fetch_all(query, params=None):
    """Execute a query and return all rows as a list of dictionaries."""
    query, params = _convert_params(query, params)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        result = cursor.fetchall()
        return _rows_to_dicts(result)
    finally:
        conn.close()


def execute_query(query, params=None):
    """Execute an INSERT, UPDATE, or DELETE query and return affected rows."""
    query, params = _convert_params(query, params)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def execute_insert(query, params=None):
    """Execute an INSERT query and return the last inserted ID."""
    query, params = _convert_params(query, params)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def init_sqlite_db():
    """Create tables and seed data for SQLite on first run."""
    if not USE_SQLITE:
        return

    db_path = _get_db_path()
    if os.path.exists(db_path):
        return

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT,
        specialization TEXT NOT NULL,
        qualification TEXT,
        experience_years INTEGER DEFAULT 0,
        consultation_fee REAL DEFAULT 500.00,
        availability TEXT DEFAULT 'Available',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS receptionists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT,
        shift TEXT DEFAULT 'Morning',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        date_of_birth DATE NOT NULL,
        gender TEXT NOT NULL,
        email TEXT,
        phone TEXT NOT NULL,
        address TEXT,
        blood_group TEXT,
        allergies TEXT,
        medical_history TEXT,
        assigned_doctor_id INTEGER,
        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (assigned_doctor_id) REFERENCES doctors(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        appointment_date DATE NOT NULL,
        appointment_time TIME NOT NULL,
        status TEXT DEFAULT 'Scheduled',
        reason TEXT,
        notes TEXT,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
        FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id INTEGER NOT NULL,
        patient_id INTEGER NOT NULL,
        doctor_id INTEGER NOT NULL,
        diagnosis TEXT NOT NULL,
        prescription_text TEXT NOT NULL,
        medicine_details TEXT,
        notes TEXT,
        prescribed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE,
        FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
        FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER NOT NULL,
        appointment_id INTEGER,
        consultation_fee REAL DEFAULT 0.00,
        medicine_charges REAL DEFAULT 0.00,
        lab_charges REAL DEFAULT 0.00,
        other_charges REAL DEFAULT 0.00,
        total_amount REAL NOT NULL,
        payment_status TEXT DEFAULT 'Unpaid',
        payment_method TEXT DEFAULT 'Cash',
        bill_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
        FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE SET NULL
    );

    CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);
    CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
    CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id);
    CREATE INDEX IF NOT EXISTS idx_appointments_doctor ON appointments(doctor_id);
    CREATE INDEX IF NOT EXISTS idx_bills_patient ON bills(patient_id);
    CREATE INDEX IF NOT EXISTS idx_bills_status ON bills(payment_status);
    CREATE INDEX IF NOT EXISTS idx_prescriptions_patient ON prescriptions(patient_id);
    CREATE INDEX IF NOT EXISTS idx_patients_name ON patients(first_name, last_name);
    """)

    from datetime import date, timedelta
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    cur.executemany("INSERT INTO admins (username, password, full_name, email, phone) VALUES (?,?,?,?,?)",
        [("admin", "admin123", "System Administrator", "admin@hospital.com", "9876543210")])

    cur.executemany("INSERT INTO doctors (username, password, full_name, email, phone, specialization, qualification, experience_years, consultation_fee, availability) VALUES (?,?,?,?,?,?,?,?,?,?)",
        [
            ("dr.smith", "doctor123", "Dr. Rajesh Smith", "dr.smith@hospital.com", "9876543211", "General Physician", "MBBS, MD", 15, 800.00, "Available"),
            ("dr.patel", "doctor123", "Dr. Ananya Patel", "dr.patel@hospital.com", "9876543212", "Cardiologist", "MBBS, DM Cardiology", 12, 1200.00, "Available"),
            ("dr.kumar", "doctor123", "Dr. Vikram Kumar", "dr.kumar@hospital.com", "9876543213", "Orthopedic Surgeon", "MBBS, MS Ortho", 20, 1500.00, "Available"),
            ("dr.sharma", "doctor123", "Dr. Priya Sharma", "dr.sharma@hospital.com", "9876543214", "Pediatrician", "MBBS, MD Pediatrics", 8, 900.00, "Available"),
            ("dr.reddy", "doctor123", "Dr. Suresh Reddy", "dr.reddy@hospital.com", "9876543215", "Dermatologist", "MBBS, MD Dermatology", 10, 1000.00, "On Leave"),
        ])

    cur.executemany("INSERT INTO receptionists (username, password, full_name, email, phone, shift) VALUES (?,?,?,?,?,?)",
        [
            ("rec.jane", "rec123", "Jane Doe", "rec.jane@hospital.com", "9876543220", "Morning"),
            ("rec.mike", "rec123", "Michael Ross", "rec.mike@hospital.com", "9876543221", "Evening"),
            ("rec.sara", "rec123", "Sara Williams", "rec.sara@hospital.com", "9876543222", "Morning"),
        ])

    cur.executemany("INSERT INTO patients (first_name, last_name, date_of_birth, gender, email, phone, address, blood_group, allergies, medical_history, assigned_doctor_id) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        [
            ("Amit", "Verma", "1990-05-15", "Male", "amit.verma@email.com", "9876543230", "12 MG Road, Delhi", "O+", "Penicillin", "Hypertension", 1),
            ("Sneha", "Gupta", "1985-08-22", "Female", "sneha.gupta@email.com", "9876543231", "45 Park Street, Kolkata", "A+", "None", "Diabetes Type 2", 2),
            ("Rahul", "Jain", "1978-01-10", "Male", "rahul.jain@email.com", "9876543232", "78 Civil Lines, Jaipur", "B+", "Aspirin", "Asthma", 1),
            ("Priyanka", "Nair", "1995-12-03", "Female", "priyanka.nair@email.com", "9876543233", "23 Marine Drive, Mumbai", "AB+", "None", "No major illnesses", 4),
            ("Arjun", "Singh", "1982-07-18", "Male", "arjun.singh@email.com", "9876543234", "56 Anna Salai, Chennai", "O-", "Sulfa drugs", "Chronic back pain", 3),
            ("Meera", "Iyer", "1993-03-25", "Female", "meera.iyer@email.com", "9876543235", "89 Residency Road, Bangalore", "A-", "None", "Migraine", 2),
            ("Karthik", "Menon", "1970-11-30", "Male", "karthik.menon@email.com", "9876543236", "34 MG Road, Kochi", "B-", "None", "Heart disease", 2),
            ("Divya", "Choudhary", "1988-09-14", "Female", "divya.c@email.com", "9876543237", "67 Civil Lines, Lucknow", "O+", "Ibuprofen", "Allergic rhinitis", 1),
        ])

    cur.executemany("INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, status, reason, notes, created_by) VALUES (?,?,?,?,?,?,?,?)",
        [
            (1, 1, today, "09:00:00", "Scheduled", "Regular checkup", None, 1),
            (2, 2, today, "10:00:00", "Scheduled", "Heart palpitations", None, 1),
            (3, 1, today, "11:00:00", "Completed", "Breathing difficulty", "Prescribed inhaler", 1),
            (4, 4, today, "09:30:00", "Scheduled", "Child vaccination", None, 2),
            (5, 3, today, "14:00:00", "Scheduled", "Back pain follow-up", None, 1),
            (6, 2, tomorrow, "10:00:00", "Scheduled", "Migraine follow-up", None, 2),
            (7, 2, yesterday, "11:00:00", "Completed", "Chest pain", "ECG done, follow-up needed", 1),
            (8, 1, yesterday, "15:00:00", "Completed", "Cold and cough", "Viral infection", 3),
            (1, 3, tomorrow, "09:00:00", "Scheduled", "Knee pain", None, 2),
            (3, 1, yesterday, "10:00:00", "Cancelled", "Routine checkup", "Patient cancelled", 1),
        ])

    cur.executemany("INSERT INTO prescriptions (appointment_id, patient_id, doctor_id, diagnosis, prescription_text, medicine_details, notes) VALUES (?,?,?,?,?,?,?)",
        [
            (3, 3, 1, "Mild asthma exacerbation", "Use inhaler twice daily for 2 weeks.", "Salbutamol Inhaler - 2 puffs twice daily\nMontair LC - 1 tablet daily", "Follow up in 2 weeks."),
            (7, 7, 2, "Chest pain - Musculoskeletal", "ECG normal. Prescribed pain relief.", "Crocin 500mg - 1 tablet TID\nPantop 40mg - 1 tablet before breakfast", "Follow up in 3 days."),
            (8, 8, 1, "Viral upper respiratory infection", "Complete rest. Stay hydrated.", "Paracetamol 650mg - TID\nCetirizine 10mg - at bedtime", "Recovery in 5-7 days."),
        ])

    cur.executemany("INSERT INTO bills (patient_id, appointment_id, consultation_fee, medicine_charges, lab_charges, other_charges, total_amount, payment_status, payment_method) VALUES (?,?,?,?,?,?,?,?,?)",
        [
            (3, 3, 800.00, 450.00, 0.00, 0.00, 1250.00, "Paid", "Cash"),
            (7, 7, 1200.00, 320.00, 500.00, 0.00, 2020.00, "Paid", "Card"),
            (8, 8, 800.00, 280.00, 0.00, 0.00, 1080.00, "Paid", "UPI"),
            (1, None, 800.00, 0.00, 0.00, 0.00, 800.00, "Unpaid", "Cash"),
            (2, None, 1200.00, 0.00, 1000.00, 0.00, 2200.00, "Partial", "Insurance"),
        ])

    conn.commit()
    conn.close()
