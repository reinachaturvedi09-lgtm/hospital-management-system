# Hospital Management System

A comprehensive, role-based Hospital Management System built with Flask, MySQL, and Bootstrap 5. Designed as a production-style 3rd-year B.Tech IT Software Engineering project, it features modular architecture, clean code, and an intuitive UI.

## Features

### Admin
- Secure login/logout with session management
- Dashboard with live statistics
- Add, edit, and delete doctors and receptionists
- View all patients and appointments
- View billing records
- Search and filter across all modules

### Doctor
- Login with role-based access
- Dashboard with today's appointments
- View patient medical history
- Add diagnosis and prescriptions
- Update appointment status (Completed / No-Show)

### Receptionist
- Login with role-based access
- Dashboard with quick actions
- Register new patients
- Book, reschedule, and cancel appointments
- Update patient details
- Generate and print bills

### General
- Responsive UI (mobile, tablet, desktop)
- Flash notifications for all actions
- Input validation on client and server side
- Pagination for large datasets
- Search functionality across modules
- Custom error pages (404, 500)
- Dark mode toggle

## Technologies Used

| Layer      | Technology                          |
|------------|-------------------------------------|
| Frontend   | HTML5, CSS3, JavaScript, Bootstrap 5, Bootstrap Icons |
| Backend    | Python 3, Flask                     |
| Database   | MySQL 8                             |
| Version Control | Git & GitHub                   |
| IDE        | VS Code                             |

## Folder Structure

```
Hospital-Management-System/
├── app.py                  # Main Flask application entry point
├── config.py               # Configuration settings (DB, secret key)
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore rules
├── README.md               # Project documentation
│
├── database/
│   ├── schema.sql          # Database table definitions
│   └── sample_data.sql     # Sample data for testing
│
├── models/
│   ├── __init__.py         # Package init, DB connection helper
│   └── db.py               # MySQL connection and query helpers
│
├── routes/
│   ├── __init__.py         # Package init, blueprint registration
│   ├── auth.py             # Login / logout routes
│   ├── admin.py            # Admin management routes
│   ├── doctor.py           # Doctor module routes
│   ├── receptionist.py     # Receptionist module routes
│   ├── patient.py          # Patient management routes
│   ├── appointment.py      # Appointment booking routes
│   └── billing.py          # Billing and invoice routes
│
├── templates/
│   ├── base.html           # Base layout with sidebar and navbar
│   ├── login.html          # Login page
│   ├── dashboard_admin.html    # Admin dashboard
│   ├── dashboard_doctor.html   # Doctor dashboard
│   ├── dashboard_receptionist.html # Receptionist dashboard
│   ├── doctors.html        # Doctor list
│   ├── doctor_form.html    # Add/edit doctor form
│   ├── receptionists.html  # Receptionist list
│   ├── receptionist_form.html # Add/edit receptionist form
│   ├── patients.html       # Patient list
│   ├── patient_form.html   # Add/edit patient form
│   ├── patient_view.html   # Patient detail view
│   ├── appointments.html   # Appointment list
│   ├── appointment_form.html # Book/edit appointment
│   ├── bills.html          # Billing list
│   ├── bill_form.html      # Generate/edit bill
│   ├── bill_print.html     # Printable invoice
│   ├── prescriptions.html  # Prescription list
│   ├── prescription_form.html # Add/edit prescription
│   ├── 404.html            # Page not found
│   └── 500.html            # Internal server error
│
├── static/
│   ├── css/
│   │   └── style.css       # Custom styles
│   ├── js/
│   │   └── script.js       # Custom JavaScript
│   └── images/             # Static images
│
├── screenshots/            # Application screenshots
│
└── docs/
    ├── SRS.pdf             # Software Requirements Specification
    ├── ER_Diagram.png      # Entity-Relationship Diagram
    ├── Use_Case_Diagram.png    # Use Case Diagram
    ├── Class_Diagram.png   # Class Diagram
    ├── Sequence_Diagram.png # Sequence Diagram
    ├── Activity_Diagram.png # Activity Diagram
    └── Flowchart.png       # System Flowchart
```
## Installation Guide

### Prerequisites
- Python 3.8 or higher
- MySQL 8.0 or higher
- pip (Python package manager)
- Git

### Step-by-Step Installation

```bash
# 1. Clone the repository
git clone https://github.com/reinachaturvedi09-lgtm/hospital-management-system.git
cd Hospital-Management-System

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure MySQL
# Log into MySQL and create the database
mysql -u root -p
```

```sql
CREATE DATABASE hospital_management;
USE hospital_management;
SOURCE database/schema.sql;
SOURCE database/sample_data.sql;
```

```bash
# 6. Update config.py with your MySQL credentials
# Edit config.py and set DB_USER, DB_PASSWORD, DB_HOST, DB_NAME

# 7. Run the Flask server
python app.py
```
##Screenshots

###Login Page
<img width="1743" height="852" alt="login page hms" src="https://github.com/user-attachments/assets/c5079735-365d-4aa2-959a-f18d9a733f54" />
 
    
###Admin Dashboard
<img width="1070" height="1008" alt="Gemini_Generated_Image_uyutu7uyutu7uyut" src="https://github.com/user-attachments/assets/38ed6563-6555-4d1a-a2d0-1180c48370fb" />

###Doctor Management and Patient Management Page
<img width="1070" height="1008" alt="Gemini_Generated_Image_gncffxgncffxgncf" src="https://github.com/user-attachments/assets/b90df3a6-541a-4fb4-9134-349c8dec47b0" />

###Appointment Management Page and the Billing Module
<img width="1070" height="1008" alt="Gemini_Generated_Image_v4f4lfv4f4lfv4f4" src="https://github.com/user-attachments/assets/3432b4b0-fde6-46c6-90b7-bca252b3833a" />

## Default Login Credentials

| Role         | Username  | Password  |
|--------------|-----------|-----------|
| Admin        | admin     | admin123  |
| Doctor       | dr.smith  | doctor123 |
| Receptionist | rec.jane  | rec123    |

## Database Schema

The system uses 7 normalized MySQL tables:

| Table            | Description                              |
|------------------|------------------------------------------|
| `admins`         | Admin user accounts                      |
| `doctors`        | Doctor profiles and credentials          |
| `receptionists`  | Receptionist profiles and credentials    |
| `patients`       | Patient personal and medical information |
| `appointments`   | Appointment records with status tracking |
| `prescriptions`  | Diagnosis and prescriptions per visit    |
| `bills`          | Billing records with itemized charges    |

**Key Constraints:**
- Primary keys on all tables
- Foreign keys linking appointments, prescriptions, and bills to patients and doctors
- Unique constraints on usernames and emails
- NOT NULL constraints on required fields
- ENUM types for roles and statuses

## UML Diagrams

All UML diagrams are available in the `docs/` folder:

- **ER Diagram** - Entity relationships and cardinality
- **Use Case Diagram** - Actor interactions with the system
- **Class Diagram** - Object-oriented structure
- **Sequence Diagram** - Login and appointment booking flows
- **Activity Diagram** - Patient registration workflow
- **Flowchart** - System process flow

## Future Improvements

- Email and SMS notifications for appointments
- Pharmacy inventory management module
- Lab test results module
- Multi-hospital support
- REST API for mobile app integration
- Role-based permission granular control
- Audit logging for all operations
- Dashboard with charts and analytics
- Backup and recovery system
- Docker containerization

## Learning Outcomes

- Full-stack web development with Flask and MySQL
- Role-based authentication and session management
- CRUD operations with relational database design
- Responsive UI design with Bootstrap 5
- Modular application architecture using Flask Blueprints
- Software engineering documentation (SRS, UML diagrams)
- Version control with Git
- Database normalization and constraint design

## Author

**[Your Name]**
B.Tech IT | [Your College Name]
[Your Email] | [GitHub Profile]

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
