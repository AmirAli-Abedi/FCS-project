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
        # Enhanced HTTPS detection
        is_https = (
            request.is_secure
            or request.scheme == "https"
            or request.headers.get("X-Forwarded-Proto") == "https"
            or request.environ.get("wsgi.url_scheme") == "https"
            or request.environ.get("HTTPS") == "on"
            or "https" in request.url.lower()
        )

        # Check if SSL certificates exist
        ssl_enabled = os.path.exists("ssl/cert.pem") and os.path.exists("ssl/key.pem")

        # Force HTTPS enforcement when SSL is enabled
        if not is_https and ssl_enabled:
            print(f"[SECURITY] Redirecting HTTP to HTTPS: {request.url}")
            # Build HTTPS URL
            https_url = request.url.replace("http://", "https://", 1)

            # Ensure port is included for localhost
            if "localhost" in https_url:
                if ":5000" not in https_url.split("://")[1].split("/")[0]:
                    https_url = https_url.replace(
                        "https://localhost", "https://localhost:5000"
                    )
                elif "https://localhost:" not in https_url:
                    https_url = https_url.replace(
                        "https://localhost", "https://localhost:5000"
                    )

            return redirect(https_url, code=301)

        # If SSL is enabled but still not HTTPS, show error
        if ssl_enabled and not is_https:
            from flask import jsonify, render_template_string

            if request.path.startswith("/api/"):
                return (
                    jsonify(
                        {
                            "error": "HTTPS required for secure routes",
                            "message": "Please access this endpoint via HTTPS or generate SSL certificates",
                            "current_url": request.url,
                            "is_https": is_https,
                            "ssl_enabled": ssl_enabled,
                        }
                    ),
                    403,
                )

            return (
                render_template_string(
                    """
                <h1>HTTPS Required</h1>
                <p>This secure route requires HTTPS connection.</p>
                <p>Current URL: {{ request.url }}</p>
                <p>Is HTTPS: {{ is_https }}</p>
                <p>SSL Enabled: {{ ssl_enabled }}</p>
                <p>Please access via: <strong>https://localhost:5000{{ request.path }}</strong></p>
                <p><a href="https://localhost:5000{{ request.path }}">Click here to access via HTTPS</a></p>
            """,
                    is_https=is_https,
                    ssl_enabled=ssl_enabled,
                ),
                403,
            )

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
            request.is_secure
            or request.scheme == "https"
            or request.headers.get("X-Forwarded-Proto") == "https"
        )

        # Add warning header to show insecure transmission
        response = f(*args, **kwargs)

        # If it's a Response object, add headers
        if hasattr(response, "headers"):
            response.headers["X-Security-Warning"] = (
                "Insecure HTTP connection - data transmitted in plain text!"
            )
            response.headers["X-Content-Type-Options"] = "nosniff"

        return response

    return decorated_function
