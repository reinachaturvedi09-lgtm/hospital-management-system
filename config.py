import os


class Config:
    """Application configuration settings."""

    # Flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY", "hms-secret-key-change-in-production")
    DEBUG = True

    # MySQL database configuration
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "root")
    DB_NAME = os.environ.get("DB_NAME", "hospital_management")
    DB_PORT = int(os.environ.get("DB_PORT", 3306))

    # Pagination
    ITEMS_PER_PAGE = 10
