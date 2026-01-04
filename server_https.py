"""
HTTPS Server for Secure Routes
Runs on port 8082, handles only secure routes (/secure/*)
Enforces HTTPS and proper security practices
"""
from flask import Flask
from database import init_databases
from secure_routes import secure_bp
import os

# Create Flask app for HTTPS server
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Only register secure blueprint
app.register_blueprint(secure_bp)

# Initialize databases
init_databases()

def get_ssl_context():
    """Get SSL context if certificates exist"""
    cert_path = 'ssl/cert.pem'
    key_path = 'ssl/key.pem'
    
    if os.path.exists(cert_path) and os.path.exists(key_path):
        return (cert_path, key_path)
    return None

if __name__ == '__main__':
    ssl_context = get_ssl_context()
    
    print("=" * 60)
    print("Starting HTTPS Server (Secure Routes)")
    print("=" * 60)
    print("Port: 8082")
    print("Routes: /secure/*")
    print("Protocol: HTTPS only")
    
    if ssl_context:
        print("SSL: Enabled")
        print("=" * 60)
        app.run(debug=False, host='0.0.0.0', port=8082, ssl_context=ssl_context, threaded=True)
    else:
        print("SSL: ERROR - Certificates not found!")
        print("Run './generate_cert.sh' to generate certificates")
        print("=" * 60)
        print("Server will not start without SSL certificates")
