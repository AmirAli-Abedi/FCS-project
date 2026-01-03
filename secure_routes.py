"""
SECURE ROUTES - Proper security implementation
This is how you should implement authentication and data storage in production.

Security features:
1. Password hashing with bcrypt
2. Strong encryption (AES-256) for credit cards
3. Parameterized queries (prevents SQL injection)
4. Input validation and sanitization
5. Minimal data exposure in responses
6. Session management
"""
import re
import sqlite3
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from database import get_secure_db
from encryption import strong_encrypt, strong_decrypt
import bcrypt


secure_bp = Blueprint('secure', __name__, url_prefix='/secure')


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_credit_card(card_number):
    """Validate credit card format (basic validation)"""
    # Remove spaces and dashes
    card_number = re.sub(r'[\s-]', '', card_number)
    # Check if it's 13-19 digits
    return re.match(r'^\d{13,19}$', card_number) is not None


def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    return True, "Password is valid"


@secure_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    SECURE REGISTRATION ENDPOINT
    
    Security features:
    - Password hashing with bcrypt (includes salt automatically)
    - Strong AES-256 encryption for credit card
    - Input validation
    - Parameterized queries (prevents SQL injection)
    """
    if request.method == 'GET':
        return render_template('register.html', version='secure')
    
    # Get and sanitize form data
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    email = request.form.get('email', '').strip()
    credit_card = request.form.get('credit_card', '').strip()
    
    # SECURE: Input validation
    if not username or not password or not email or not credit_card:
        return jsonify({'error': 'All fields are required'}), 400
    
    # SECURE: Validate username (alphanumeric and underscore only)
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        return jsonify({'error': 'Username must be 3-20 characters, alphanumeric and underscore only'}), 400
    
    # SECURE: Validate email format
    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # SECURE: Validate password strength
    is_valid, message = validate_password(password)
    if not is_valid:
        return jsonify({'error': message}), 400
    
    # SECURE: Validate credit card format
    if not validate_credit_card(credit_card):
        return jsonify({'error': 'Invalid credit card format'}), 400
    
    # SECURE: Hash password with bcrypt (includes salt automatically)
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # SECURE: Encrypt credit card with AES-256
    credit_card_encrypted = strong_encrypt(credit_card)
    
    conn = get_secure_db()
    cursor = conn.cursor()
    
    try:
        # SECURE: Parameterized query prevents SQL injection
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, credit_card_encrypted)
            VALUES (?, ?, ?, ?)
        ''', (username, password_hash, email, credit_card_encrypted))
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id
        }), 201
        
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Username already exists'}), 400
    except Exception as e:
        conn.close()
        return jsonify({'error': f'Registration error: {str(e)}'}), 500


@secure_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    SECURE LOGIN ENDPOINT
    
    Security features:
    - Parameterized queries (prevents SQL injection)
    - Password verification using bcrypt
    - Minimal data exposure
    - Session management
    """
    if request.method == 'GET':
        return render_template('login.html', version='secure')
    
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    conn = get_secure_db()
    cursor = conn.cursor()
    
    try:
        # SECURE: Parameterized query prevents SQL injection
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # SECURE: Verify password using bcrypt
            if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                # SECURE: Store minimal data in session
                session['user_id'] = user['id']
                session['username'] = user['username']
                
                # SECURE: Return only safe, non-sensitive data
                return jsonify({
                    'message': 'Login successful',
                    'user': {
                        'id': user['id'],
                        'username': user['username'],
                        'email': user['email']
                        # SECURE: Password and credit card NOT included in response
                    }
                }), 200
            else:
                return jsonify({'error': 'Invalid credentials'}), 401
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        conn.close()
        return jsonify({'error': f'Login error: {str(e)}'}), 500


@secure_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    SECURE USER DATA ENDPOINT
    
    Security features:
    - Authentication check
    - Authorization check (users can only see their own data)
    - Parameterized queries
    - Minimal data exposure
    """
    # SECURE: Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    # SECURE: Authorization check - users can only access their own data
    if session['user_id'] != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    conn = get_secure_db()
    cursor = conn.cursor()
    
    # SECURE: Parameterized query prevents SQL injection
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        # SECURE: Return only safe data, never expose password or credit card
        return jsonify({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'created_at': user['created_at']
            # SECURE: Password hash and encrypted credit card NOT exposed
        }), 200
    else:
        return jsonify({'error': 'User not found'}), 404


@secure_bp.route('/users', methods=['GET'])
def list_users():
    """
    SECURE USER LIST ENDPOINT
    
    Security features:
    - Authentication required
    - Minimal data exposure (no passwords or credit cards)
    """
    # SECURE: Require authentication
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    conn = get_secure_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email, created_at FROM users')
    users = cursor.fetchall()
    conn.close()
    
    # SECURE: Return only safe data, never passwords or credit cards
    user_list = []
    for user in users:
        user_list.append({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'created_at': user['created_at']
            # SECURE: Password and credit card NOT included
        })
    
    return jsonify({'users': user_list}), 200


@secure_bp.route('/logout', methods=['POST'])
def logout():
    """Secure logout - clears session"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

