"""
INSECURE ROUTES - Demonstrating security vulnerabilities
DO NOT USE THIS CODE IN PRODUCTION!

This module demonstrates common security vulnerabilities:
1. Plain text password storage
2. Weak encryption (base64)
3. SQL injection vulnerabilities
4. No input validation
5. Exposed sensitive data in responses
6. Insecure transmission (HTTP)
"""
import sqlite3
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from database import get_insecure_db
from encryption import weak_encrypt, weak_decrypt

insecure_bp = Blueprint('insecure', __name__, url_prefix='/insecure')


@insecure_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    VULNERABLE REGISTRATION ENDPOINT
    
    Vulnerabilities:
    - Stores password in plain text (no hashing)
    - Uses weak encryption (base64) for credit card
    - No input validation
    - SQL injection possible (though we use parameterized queries here for safety)
    """
    if request.method == 'GET':
        return render_template('register.html', version='insecure')
    
    # Get form data
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')  # VULNERABILITY: No validation
    email = request.form.get('email', '').strip()
    credit_card = request.form.get('credit_card', '').strip()
    
    # VULNERABILITY: No input validation
    if not username or not password or not email or not credit_card:
        return jsonify({'error': 'All fields required'}), 400
    
    conn = get_insecure_db()
    cursor = conn.cursor()
    
    try:
        # VULNERABILITY: Password stored in plain text!
        # VULNERABILITY: Credit card "encrypted" with weak base64 encoding
        cursor.execute('''
            INSERT INTO users (username, password, email, credit_card)
            VALUES (?, ?, ?, ?)
        ''', (username, password, email, weak_encrypt(credit_card)))
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id,
            'warning': 'This is an insecure implementation!'
        }), 201
        
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Username already exists'}), 400
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500


@insecure_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    VULNERABLE LOGIN ENDPOINT
    
    Vulnerabilities:
    - SQL injection vulnerability (direct string concatenation)
    - Plain text password comparison
    - Exposes user data in response
    """
    if request.method == 'GET':
        return render_template('login.html', version='insecure')
    
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    
    # VULNERABILITY: SQL Injection - Direct string concatenation!
    # This allows attackers to inject SQL code
    # Example: username = "admin' OR '1'='1" would bypass authentication
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    
    conn = get_insecure_db()
    cursor = conn.cursor()
    
    try:
        # VULNERABILITY: Executing raw SQL with string concatenation
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # VULNERABILITY: Returning full user object including password!
            session['user_id'] = user['id']
            session['username'] = user['username']
            
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'password': user['password'],  # VULNERABILITY: Exposing password!
                    'credit_card': weak_decrypt(user['credit_card'])  # VULNERABILITY: Exposing decrypted credit card!
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        conn.close()
        return jsonify({'error': f'Login error: {str(e)}'}), 500


@insecure_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    VULNERABLE USER DATA ENDPOINT
    
    Vulnerabilities:
    - Exposes all user data including passwords
    - No authentication/authorization check
    - SQL injection possible
    """
    conn = get_insecure_db()
    cursor = conn.cursor()
    
    # VULNERABILITY: No authentication check - anyone can access any user's data!
    # VULNERABILITY: Potential SQL injection if user_id is not properly validated
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    user = cursor.fetchone()
    conn.close()
    
    if user:
        # VULNERABILITY: Returning sensitive data including password and decrypted credit card!
        return jsonify({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'password': user['password'],  # VULNERABILITY: Exposing plain text password!
            'credit_card': weak_decrypt(user['credit_card']),  # VULNERABILITY: Exposing credit card!
            'created_at': user['created_at']
        }), 200
    else:
        return jsonify({'error': 'User not found'}), 404


@insecure_bp.route('/users', methods=['GET'])
def list_users():
    """
    VULNERABLE USER LIST ENDPOINT
    
    Vulnerabilities:
    - Exposes all users' sensitive data
    - No access control
    """
    conn = get_insecure_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    
    # VULNERABILITY: Exposing all users' passwords and credit cards!
    user_list = []
    for user in users:
        user_list.append({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'password': user['password'],  # VULNERABILITY: Exposing passwords!
            'credit_card': weak_decrypt(user['credit_card']),  # VULNERABILITY: Exposing credit cards!
            'created_at': user['created_at']
        })
    
    return jsonify({'users': user_list}), 200


@insecure_bp.route('/logout', methods=['POST'])
def logout():
    """Simple logout"""
    session.clear()
    return jsonify({'message': 'Logged out'}), 200

