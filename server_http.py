"""
HTTP Server for Insecure Routes
Runs on port 8081, handles only insecure routes (/insecure/*)
Demonstrates security vulnerabilities with HTTP only
"""
from flask import Flask
from database import init_databases
from insecure_routes import insecure_bp
import os

# Create Flask app for HTTP server
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Only register insecure blueprint
app.register_blueprint(insecure_bp)

# Initialize databases
init_databases()

if __name__ == '__main__':
    print("=" * 60)
    print("Starting HTTP Server (Insecure Routes)")
    print("=" * 60)
    print("Port: 8081")
    print("Routes: /insecure/*")
    print("Protocol: HTTP only")
    print("=" * 60)
    
    # Run HTTP server (no SSL)
    app.run(debug=False, host='0.0.0.0', port=8081, threaded=True)
