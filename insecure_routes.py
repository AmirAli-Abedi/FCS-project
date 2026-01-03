"""
INSECURE ROUTES - Demonstrating security vulnerabilities
DO NOT USE THIS CODE IN PRODUCTION!

This module demonstrates common security vulnerabilities:
1. Plain text password storage
2. Weak encryption (base64)
3. SQL injection vulnerabilities
4. No input validation
5. Exposed sensitive data in responses
6. Insecure transmission (HTTP) - VULNERABILITY: Data sent in plain text!
"""
import sqlite3
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, make_response
from database import get_insecure_db
from encryption import weak_encrypt, weak_decrypt

insecure_bp = Blueprint('insecure', __name__, url_prefix='/insecure')


def add_http_warning(response):
    """
    Add HTTP warning headers to demonstrate insecure transmission vulnerability.
    VULNERABILITY: HTTP transmits data in plain text - anyone can intercept it!
    """
    if isinstance(response, tuple):
        # Handle (response, status_code) tuples
        resp, status = response
        response = make_response(resp)
        response.status_code = status
    
    if hasattr(response, 'headers'):
        response.headers['X-Security-Warning'] = 'INSECURE: HTTP connection - data transmitted in plain text!'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # Check if actually using HTTP
        is_https = (
            request.is_secure or 
            request.scheme == 'https' or
            request.headers.get('X-Forwarded-Proto') == 'https'
        )
        if not is_https:
            response.headers['X-Protocol'] = 'HTTP (INSECURE)'
        else:
            response.headers['X-Protocol'] = 'HTTPS (but this route should use HTTP to show vulnerability)'
    
    return response


@insecure_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    VULNERABLE REGISTRATION ENDPOINT
    
    Vulnerabilities:
    - Stores password in plain text (no hashing)
    - Uses weak encryption (base64) for credit card
    - No input validation
    - SQL injection possible (though we use parameterized queries here for safety)
    - VULNERABILITY: HTTP transmission - data sent in plain text!
    """
    if request.method == 'GET':
        return add_http_warning(render_template('register.html', version='insecure'))
    
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
        
        response = jsonify({
            'message': 'User registered successfully',
            'user_id': user_id,
            'warning': 'This is an insecure implementation!',
            'http_warning': 'VULNERABILITY: Data transmitted over HTTP in plain text!'
        })
        return add_http_warning((response, 201))
        
    except sqlite3.IntegrityError:
        conn.close()
        return add_http_warning((jsonify({'error': 'Username already exists'}), 400))
    except Exception as e:
        conn.close()
        return add_http_warning((jsonify({'error': str(e)}), 500))


@insecure_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    VULNERABLE LOGIN ENDPOINT
    
    Vulnerabilities:
    - SQL injection vulnerability (direct string concatenation)
    - Plain text password comparison
    - Exposes user data in response
    - VULNERABILITY: HTTP transmission - credentials sent in plain text!
    """
    if request.method == 'GET':
        return add_http_warning(render_template('login.html', version='insecure'))
    
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    
    # VULNERABILITY: SQL Injection - Direct string concatenation!
    # This allows attackers to inject SQL code
    # Example: username = "admin' OR '1'='1' --" would bypass authentication
    # The -- comments out the password check, making the query always return true
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
            
            response = jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'password': user['password'],  # VULNERABILITY: Exposing password!
                    'credit_card': weak_decrypt(user['credit_card'])  # VULNERABILITY: Exposing decrypted credit card!
                },
                'http_warning': 'VULNERABILITY: Credentials transmitted over HTTP in plain text!'
            })
            return add_http_warning((response, 200))
        else:
            return add_http_warning((jsonify({'error': 'Invalid credentials'}), 401))
            
    except Exception as e:
        conn.close()
        return add_http_warning((jsonify({'error': f'Login error: {str(e)}'}), 500))


@insecure_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    VULNERABLE USER DATA ENDPOINT
    
    Vulnerabilities:
    - Exposes all user data including passwords
    - No authentication/authorization check
    - SQL injection possible
    - VULNERABILITY: HTTP transmission - sensitive data sent in plain text!
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
        response = jsonify({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'password': user['password'],  # VULNERABILITY: Exposing plain text password!
            'credit_card': weak_decrypt(user['credit_card']),  # VULNERABILITY: Exposing credit card!
            'created_at': user['created_at'],
            'http_warning': 'VULNERABILITY: Sensitive data transmitted over HTTP in plain text!'
        })
        return add_http_warning((response, 200))
    else:
        return add_http_warning((jsonify({'error': 'User not found'}), 404))


@insecure_bp.route('/users', methods=['GET'])
def list_users():
    """
    VULNERABLE USER LIST ENDPOINT
    
    Vulnerabilities:
    - Exposes all users' sensitive data
    - No access control
    - VULNERABILITY: HTTP transmission - all data sent in plain text!
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
    
    response = jsonify({
        'users': user_list,
        'http_warning': 'VULNERABILITY: All user data transmitted over HTTP in plain text!'
    })
    return add_http_warning((response, 200))


@insecure_bp.route('/logout', methods=['POST'])
def logout():
    """Simple logout (HTTP - insecure transmission)"""
    session.clear()
    return add_http_warning((jsonify({'message': 'Logged out'}), 200))

