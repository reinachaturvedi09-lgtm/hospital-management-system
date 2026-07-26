"""
Configuration file for Hospital Management System
Contains database and Flask configuration settings
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Flask Configuration
DEBUG = True
SECRET_KEY = 'your-secret-key-change-this-in-production'

# MySQL Database Configuration
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DB = os.getenv('MYSQL_DB', 'hospital_management')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))

# Session Configuration
PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
SESSION_REFRESH_EACH_REQUEST = True

# Pagination
ITEMS_PER_PAGE = 10
