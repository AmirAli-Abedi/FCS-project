"""
Database setup and management for both insecure and secure implementations.
Uses SQLite for simplicity - no external database server required.
"""
import sqlite3
import os


def get_insecure_db():
    """Get connection to insecure database (stores plain text data)"""
    conn = sqlite3.connect('insecure.db')
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn


def get_secure_db():
    """Get connection to secure database (stores encrypted/hashed data)"""
    conn = sqlite3.connect('secure.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_databases():
    """Initialize both databases with user tables"""
    
    # Initialize insecure database
    conn = get_insecure_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            credit_card TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    
    # Initialize secure database
    conn = get_secure_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT NOT NULL,
            credit_card_encrypted TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    
    print("Databases initialized successfully!")


def get_all_users_insecure():
    """Get all users from insecure database (for comparison page)"""
    conn = get_insecure_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return users


def get_all_users_secure():
    """Get all users from secure database (for comparison page)"""
    conn = get_secure_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return users

