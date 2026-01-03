"""
Main Flask application for Secure Computing Project
Demonstrates security vulnerabilities and their proper solutions
"""
from flask import Flask, render_template, jsonify
from database import init_databases, get_all_users_insecure, get_all_users_secure
from insecure_routes import insecure_bp
from secure_routes import secure_bp
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# Register blueprints
app.register_blueprint(insecure_bp)
app.register_blueprint(secure_bp)


@app.route('/')
def index():
    """Main page with navigation"""
    return render_template('index.html')


@app.route('/compare')
def compare():
    """Comparison page showing side-by-side database contents"""
    insecure_users = get_all_users_insecure()
    secure_users = get_all_users_secure()
    
    # Convert to dictionaries for easier template rendering
    insecure_data = []
    for user in insecure_users:
        insecure_data.append({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'password': user['password'],  # Plain text!
            'credit_card': user['credit_card']  # Weakly encrypted
        })
    
    secure_data = []
    for user in secure_users:
        secure_data.append({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'password_hash': user['password_hash'],  # Hashed!
            'credit_card_encrypted': user['credit_card_encrypted']  # Strongly encrypted
        })
    
    return render_template('compare.html', 
                         insecure_users=insecure_data,
                         secure_users=secure_data)


@app.route('/api/insecure/users')
def api_insecure_users():
    """API endpoint for insecure users (for demonstration)"""
    users = get_all_users_insecure()
    user_list = []
    for user in users:
        user_list.append({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'password': user['password'],
            'credit_card': user['credit_card']
        })
    return jsonify({'users': user_list})


@app.route('/api/secure/users')
def api_secure_users():
    """API endpoint for secure users (for demonstration)"""
    users = get_all_users_secure()
    user_list = []
    for user in users:
        user_list.append({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            # Password and credit card NOT included for security
        })
    return jsonify({'users': user_list})


if __name__ == '__main__':
    # Initialize databases on startup
    print("Initializing databases...")
    init_databases()
    print("Starting Flask application...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)

