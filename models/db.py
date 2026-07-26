"""
Database connection and query helper module.
Provides functions to connect to MySQL and perform common database operations.
"""

import pymysql
from config import Config


def get_connection():
    """Create and return a new MySQL database connection."""
    return pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        port=Config.DB_PORT,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def fetch_one(query, params=None):
    """Execute a query and return a single row as a dictionary."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()
    finally:
        conn.close()


def fetch_all(query, params=None):
    """Execute a query and return all rows as a list of dictionaries."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    finally:
        conn.close()


def execute_query(query, params=None):
    """Execute an INSERT, UPDATE, or DELETE query and return affected rows."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
    finally:
        conn.close()


def execute_insert(query, params=None):
    """Execute an INSERT query and return the last inserted ID."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            return cursor.lastrowid
    finally:
        conn.close()
