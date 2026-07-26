"""
Hospital Management System - Main Application
Entry point for the Flask web application.
"""

from flask import Flask, render_template
from config import Config


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    from models.db import init_sqlite_db
    init_sqlite_db()

    from routes import register_blueprints
    register_blueprints(app)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("500.html"), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
