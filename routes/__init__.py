"""
Route blueprints package.
Registers all Flask blueprints with the main application.
"""

from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.doctor import doctor_bp
from routes.receptionist import receptionist_bp
from routes.patient import patient_bp
from routes.appointment import appointment_bp
from routes.billing import billing_bp


def register_blueprints(app):
    """Register all application blueprints with the Flask app."""
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(receptionist_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(appointment_bp)
    app.register_blueprint(billing_bp)
