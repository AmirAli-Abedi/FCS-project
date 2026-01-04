"""
Reverse Proxy Server
Runs on port 8080, handles routing:
- Serves / and /compare directly
- Forwards /insecure/* to HTTP server (port 8081)
- Forwards /secure/* to HTTPS server (port 8082)
"""
from flask import Flask, render_template, request, Response, jsonify
from database import init_databases, get_all_users_insecure, get_all_users_secure
import requests
import urllib3
import os

app = Flask(__name__)

# Backend server URLs
HTTP_SERVER_URL = 'http://localhost:8081'
HTTPS_SERVER_URL = 'https://localhost:8082'

# Initialize databases (shared)
init_databases()

# Disable SSL verification warnings for local HTTPS server (self-signed cert)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def forward_request(target_url, path, method='GET', **kwargs):
    """
    Forward request to backend server
    
    Args:
        target_url: Base URL of target server
        path: Request path
        method: HTTP method
        **kwargs: Additional arguments (data, json, files, etc.)
    
    Returns:
        Response object or None if error
    """
    try:
        url = f"{target_url}{path}"
        
        # Prepare headers (exclude host and connection)
        headers = {}
        for key, value in request.headers:
            if key.lower() not in ['host', 'connection', 'content-length']:
                headers[key] = value
        
        # Prepare cookies
        cookies = dict(request.cookies)
        
        # Forward request based on method
        if method == 'GET':
            response = requests.get(
                url,
                params=request.args,
                headers=headers,
                cookies=cookies,
                allow_redirects=False,
                verify=False,  # Disable SSL verification for self-signed cert
                timeout=10
            )
        elif method == 'POST':
            # Get form data or JSON
            if request.is_json:
                response = requests.post(
                    url,
                    json=request.get_json(),
                    headers=headers,
                    cookies=cookies,
                    allow_redirects=False,
                    verify=False,
                    timeout=10
                )
            else:
                response = requests.post(
                    url,
                    data=request.form,
                    files=request.files,
                    headers=headers,
                    cookies=cookies,
                    allow_redirects=False,
                    verify=False,
                    timeout=10
                )
        else:
            # For other methods (PUT, DELETE, etc.)
            response = requests.request(
                method,
                url,
                params=request.args if method == 'GET' else None,
                data=request.get_data() if method != 'GET' else None,
                headers=headers,
                cookies=cookies,
                allow_redirects=False,
                verify=False,
                timeout=10
            )
        
        # Create Flask response from requests response
        flask_response = Response(
            response.content,
            status=response.status_code,
            headers=dict(response.headers)
        )
        
        # Copy cookies from backend response
        for cookie in response.cookies:
            flask_response.set_cookie(
                cookie.name,
                cookie.value,
                domain=cookie.domain,
                path=cookie.path,
                secure=cookie.secure,
                httponly=cookie.has_nonstandard_attr('HttpOnly')
            )
        
        return flask_response
        
    except requests.exceptions.ConnectionError:
        return jsonify({
            'error': 'Backend server unavailable',
            'message': f'Cannot connect to {target_url}. Is the server running?'
        }), 503
    except requests.exceptions.Timeout:
        return jsonify({
            'error': 'Request timeout',
            'message': 'Backend server did not respond in time'
        }), 504
    except Exception as e:
        return jsonify({
            'error': 'Proxy error',
            'message': str(e)
        }), 500


@app.route('/')
def index():
    """Main page - served directly by proxy"""
    # Check if using HTTPS
    is_https = (
        request.is_secure
        or request.scheme == 'https'
        or request.headers.get('X-Forwarded-Proto') == 'https'
    )
    return render_template('index.html', is_https=is_https)


@app.route('/compare')
def compare():
    """Comparison page - served directly by proxy"""
    insecure_users = get_all_users_insecure()
    secure_users = get_all_users_secure()
    
    # Check if using HTTPS
    is_https = (
        request.is_secure
        or request.scheme == 'https'
        or request.headers.get('X-Forwarded-Proto') == 'https'
    )
    
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
    
    return render_template(
        'compare.html',
        insecure_users=insecure_data,
        secure_users=secure_data,
        is_https=is_https
    )


@app.route('/insecure/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def forward_insecure(path):
    """Forward insecure routes to HTTP server"""
    # Use the full request path
    full_path = request.path
    return forward_request(HTTP_SERVER_URL, full_path, method=request.method)


@app.route('/secure/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def forward_secure(path):
    """Forward secure routes to HTTPS server"""
    # Use the full request path
    full_path = request.path
    return forward_request(HTTPS_SERVER_URL, full_path, method=request.method)


@app.route('/api/insecure/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def forward_api_insecure(path):
    """Forward insecure API routes to HTTP server"""
    full_path = f'/api/insecure/{path}'
    return forward_request(HTTP_SERVER_URL, full_path, method=request.method)


@app.route('/api/secure/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def forward_api_secure(path):
    """Forward secure API routes to HTTPS server"""
    full_path = f'/api/secure/{path}'
    return forward_request(HTTPS_SERVER_URL, full_path, method=request.method)


@app.route('/health')
def health():
    """Health check endpoint"""
    # Check if backend servers are running
    http_status = 'unknown'
    https_status = 'unknown'
    
    try:
        response = requests.get(f'{HTTP_SERVER_URL}/insecure/register', timeout=2, verify=False)
        http_status = 'up' if response.status_code < 500 else 'error'
    except:
        http_status = 'down'
    
    try:
        response = requests.get(f'{HTTPS_SERVER_URL}/secure/register', timeout=2, verify=False)
        https_status = 'up' if response.status_code < 500 else 'error'
    except:
        https_status = 'down'
    
    return jsonify({
        'proxy': 'up',
        'http_server': http_status,
        'https_server': https_status
    })


if __name__ == '__main__':
    print("=" * 60)
    print("Starting Reverse Proxy Server")
    print("=" * 60)
    print("Port: 8080")
    print("Routes:")
    print("  / -> Served directly")
    print("  /compare -> Served directly")
    print("  /insecure/* -> Forwarded to HTTP server (port 8081)")
    print("  /secure/* -> Forwarded to HTTPS server (port 8082)")
    print("=" * 60)
    print("\nMake sure HTTP and HTTPS servers are running!")
    print("=" * 60)
    
    app.run(debug=False, host='0.0.0.0', port=8080, threaded=True)

