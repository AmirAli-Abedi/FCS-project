"""
HTTPS Enforcement Middleware
Enforces HTTPS on secure routes while allowing HTTP on insecure routes
"""
from functools import wraps
from flask import request, redirect, url_for, current_app
import os


def require_https(f):
    """
    Decorator to enforce HTTPS on secure routes.
    If request comes via HTTP, redirects to HTTPS version.
    
    Usage:
        @secure_bp.route('/login')
        @require_https
        def login():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if request is secure (HTTPS)
        # Multiple methods to detect HTTPS:
        # 1. request.is_secure (works behind proxy)
        # 2. request.scheme (should be 'https')
        # 3. X-Forwarded-Proto header (proxy header)
        # 4. wsgi.url_scheme from environ (direct Flask SSL)
        # 5. Check if SSL certificates exist (app running with SSL)
        is_https = (
            request.is_secure or 
            request.scheme == 'https' or
            request.headers.get('X-Forwarded-Proto') == 'https' or
            request.environ.get('wsgi.url_scheme') == 'https' or
            request.environ.get('HTTPS') == 'on'
        )
        
        # Also check if app is configured with SSL by checking for cert files
        # If SSL is enabled, we should enforce HTTPS
        ssl_enabled = (
            os.path.exists('ssl/cert.pem') and 
            os.path.exists('ssl/key.pem')
        )
        
        if not is_https:
            # If SSL is enabled but request is HTTP, redirect to HTTPS
            if ssl_enabled:
                # Build HTTPS URL - replace http with https
                https_url = request.url.replace('http://', 'https://', 1)
                # Ensure port is included
                if 'localhost' in https_url and ':5000' not in https_url.split('://')[1].split('/')[0]:
                    https_url = https_url.replace('https://localhost', 'https://localhost:5000')
                return redirect(https_url, code=301)  # 301 = Permanent redirect
            else:
                # SSL not enabled - for demo, show error message
                from flask import jsonify
                if request.path.startswith('/api/'):
                    return jsonify({
                        'error': 'HTTPS required for secure routes',
                        'message': 'Please access this endpoint via HTTPS or generate SSL certificates'
                    }), 403
                # For HTML pages, show error
                from flask import render_template_string
                return render_template_string('''
                    <h1>HTTPS Required</h1>
                    <p>This secure route requires HTTPS connection.</p>
                    <p>Please access via: <strong>https://localhost:5000{{ request.path }}</strong></p>
                    <p>Or generate SSL certificates by running: <code>./generate_cert.sh</code></p>
                '''), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def allow_http_only(f):
    """
    Decorator for insecure routes that should only work on HTTP.
    Adds warning headers to demonstrate insecure transmission.
    
    Usage:
        @insecure_bp.route('/login')
        @allow_http_only
        def login():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if request is HTTPS
        is_https = (
            request.is_secure or 
            request.scheme == 'https' or
            request.headers.get('X-Forwarded-Proto') == 'https'
        )
        
        # Add warning header to show insecure transmission
        response = f(*args, **kwargs)
        
        # If it's a Response object, add headers
        if hasattr(response, 'headers'):
            response.headers['X-Security-Warning'] = 'Insecure HTTP connection - data transmitted in plain text!'
            response.headers['X-Content-Type-Options'] = 'nosniff'
        
        return response
    
    return decorated_function

