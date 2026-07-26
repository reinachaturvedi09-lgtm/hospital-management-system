"""
Authentication routes.
Handles login, logout, and session management for all user roles.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.db import fetch_one

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["GET", "POST"])
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Display login page and handle authentication for all roles."""
    if "role" in session:
        return redirect(url_for(get_redirect_url(session["role"])))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "").strip()

        if not username or not password or not role:
            flash("All fields are required.", "danger")
            return render_template("login.html")

        user = None
        if role == "admin":
            user = fetch_one(
                "SELECT * FROM admins WHERE username = %s AND password = %s",
                (username, password),
            )
        elif role == "doctor":
            user = fetch_one(
                "SELECT * FROM doctors WHERE username = %s AND password = %s",
                (username, password),
            )
        elif role == "receptionist":
            user = fetch_one(
                "SELECT * FROM receptionists WHERE username = %s AND password = %s",
                (username, password),
            )

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["full_name"] = user["full_name"]
            session["role"] = role
            flash(f"Welcome, {user['full_name']}!", "success")
            return redirect(url_for(get_redirect_url(role)))
        else:
            flash("Invalid credentials. Please try again.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    """Clear session and redirect to login page."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


def get_redirect_url(role):
    """Return the appropriate dashboard URL based on user role."""
    urls = {
        "admin": "admin.dashboard",
        "doctor": "doctor.dashboard",
        "receptionist": "receptionist.dashboard",
    }
    return urls.get(role, "auth.login")
