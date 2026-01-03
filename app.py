"""
Main Flask application for Secure Computing Project
Demonstrates security vulnerabilities and their proper solutions

Supports both HTTP and HTTPS:
- Insecure routes (/insecure/*) - Use HTTP to demonstrate vulnerability
- Secure routes (/secure/*) - Enforce HTTPS (redirect HTTP → HTTPS)
- Home and compare pages - Accessible on both HTTP and HTTPS
"""

from flask import Flask, render_template, jsonify, request
from database import init_databases, get_all_users_insecure, get_all_users_secure
from insecure_routes import insecure_bp
from secure_routes import secure_bp
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# Register blueprints
app.register_blueprint(insecure_bp)
app.register_blueprint(secure_bp)


@app.before_request
def log_request_info():
    """Log request information for debugging HTTPS"""
    # Flask logs show "HTTP/1.1" which is the protocol version, not HTTP vs HTTPS
    # HTTPS still uses HTTP/1.1 as the application protocol over TLS
    # So we need to check the actual connection scheme
    protocol = request.scheme
    is_secure = request.is_secure
    url_scheme = request.environ.get("wsgi.url_scheme", "unknown")

    # Log with clear HTTPS/HTTP indicator
    connection_type = (
        "HTTPS"
        if (is_secure or protocol == "https" or url_scheme == "https")
        else "HTTP"
    )

    # Make the log more prominent
    print("=" * 50)
    print(f"REQUEST LOG: [{connection_type}] {request.method} {request.path}")
    print(f"  Protocol: {protocol}, Secure: {is_secure}, WSGI: {url_scheme}")
    print("=" * 50)


def get_ssl_context():
    """Get SSL context if certificates exist"""
    cert_path = "ssl/cert.pem"
    key_path = "ssl/key.pem"

    if os.path.exists(cert_path) and os.path.exists(key_path):
        return (cert_path, key_path)
    return None


# Store SSL status for middleware
app.config["SSL_ENABLED"] = get_ssl_context() is not None


@app.route("/")
def index():
    """Main page with navigation - accessible on both HTTP and HTTPS"""
    # Check if using HTTPS
    is_https = (
        request.is_secure
        or request.scheme == "https"
        or request.headers.get("X-Forwarded-Proto") == "https"
    )
    return render_template("index.html", is_https=is_https)


@app.route("/compare")
def compare():
    """Comparison page showing side-by-side database contents - accessible on both HTTP and HTTPS"""
    insecure_users = get_all_users_insecure()
    secure_users = get_all_users_secure()

    # Check if using HTTPS
    is_https = (
        request.is_secure
        or request.scheme == "https"
        or request.headers.get("X-Forwarded-Proto") == "https"
    )

    # Convert to dictionaries for easier template rendering
    insecure_data = []
    for user in insecure_users:
        insecure_data.append(
            {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "password": user["password"],  # Plain text!
                "credit_card": user["credit_card"],  # Weakly encrypted
            }
        )

    secure_data = []
    for user in secure_users:
        secure_data.append(
            {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "password_hash": user["password_hash"],  # Hashed!
                "credit_card_encrypted": user[
                    "credit_card_encrypted"
                ],  # Strongly encrypted
            }
        )

    return render_template(
        "compare.html",
        insecure_users=insecure_data,
        secure_users=secure_data,
        is_https=is_https,
    )


@app.route("/api/insecure/users")
def api_insecure_users():
    """API endpoint for insecure users (for demonstration)"""
    users = get_all_users_insecure()
    user_list = []
    for user in users:
        user_list.append(
            {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "password": user["password"],
                "credit_card": user["credit_card"],
            }
        )
    return jsonify({"users": user_list})


@app.route("/api/secure/users")
def api_secure_users():
    """API endpoint for secure users (for demonstration)"""
    users = get_all_users_secure()
    user_list = []
    for user in users:
        user_list.append(
            {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                # Password and credit card NOT included for security
            }
        )
    return jsonify({"users": user_list})


if __name__ == "__main__":
    # Initialize databases on startup
    print("Initializing databases...")
    init_databases()

    # Check for SSL certificates
    ssl_context = get_ssl_context()

    print("\n" + "=" * 60)
    print("Starting Flask application...")
    print("=" * 60)

    if ssl_context:
        print("[OK] SSL certificates found - HTTPS enabled")
        print(
            "\n[WARNING] IMPORTANT: Flask development server with SSL ONLY accepts HTTPS connections"
        )
        print("   You MUST access the application via HTTPS:")
        print("   -> https://localhost:5000")
        print("\n   HTTP connections (http://localhost:5000) will FAIL")
        print("   This is expected - Flask with SSL only serves HTTPS")
        print(
            "\n   Insecure routes: Accessible via HTTPS (but will show HTTP warnings)"
        )
        print("   Secure routes: REQUIRE HTTPS (enforced by middleware)")
        print(
            "\n[WARNING] Browser will show security warning for self-signed certificate"
        )
        print("   This is expected. Click 'Advanced' -> 'Proceed' to continue.")
        print("\n" + "=" * 60)
        # Run with SSL support - ONLY accepts HTTPS connections
        # All requests will be HTTPS - logs will show HTTPS
        app.run(debug=True, host="0.0.0.0", port=5000, ssl_context=ssl_context)
    else:
        print("[WARNING] SSL certificates not found - HTTPS disabled")
        print("   Run 'python generate_cert_simple.py' to generate certificates")
        print("\nURL:")
        print("  HTTP:  http://localhost:5000")
        print("\nNote: Secure routes will not work properly without HTTPS")
        print("      (They will allow HTTP but show warnings)")
        print("=" * 60)
        # Run without SSL (for development/testing)
        app.run(debug=True, host="0.0.0.0", port=5000)
