# Secure Computing Project: Data Disclosure and Storage Encryption

## Project Description
This project demonstrates security vulnerabilities in storing and transmitting sensitive user data (passwords and credit card information). It includes both **insecure** and **secure** implementations side-by-side for educational purposes.

## Security Vulnerabilities Demonstrated

1. **Plain text password storage** - Passwords stored directly in database
2. **Weak encryption methods** - Using base64 encoding instead of proper encryption
3. **Insecure transmission** - HTTP instead of HTTPS
4. **SQL injection** - Direct string concatenation in SQL queries
5. **Exposed sensitive data** - Full user objects including passwords in API responses
6. **No input validation** - Accepting any input without sanitization

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## HTTPS Setup (Required for Secure Routes)

This project uses **conditional HTTPS**:
- **Insecure routes** (`/insecure/*`) - Use HTTP to demonstrate vulnerability
- **Secure routes** (`/secure/*`) - Enforce HTTPS (redirects HTTP → HTTPS)
- **Home and compare pages** - Accessible on both HTTP and HTTPS

### Generate SSL Certificate

For local development, generate a self-signed certificate:

```bash
./generate_cert.sh
```

Or manually:
```bash
mkdir -p ssl
openssl req -x509 -newkey rsa:4096 -nodes \
    -out ssl/cert.pem \
    -keyout ssl/key.pem \
    -days 365 \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

**Note:** Browsers will show a security warning for self-signed certificates. This is expected for local development. Click "Advanced" → "Proceed" to continue.

## Running the Application

```bash
python app.py
```

The application will:
- Run on **HTTP** (port 5000) for insecure routes
- Run on **HTTPS** (port 5000) for secure routes (if certificates exist)
- Show both URLs in the startup message

### URLs:
- **HTTP:** `http://localhost:5000` - For insecure routes and home page
- **HTTPS:** `https://localhost:5000` - For secure routes (enforced)

**Important:** If you access secure routes via HTTP, they will automatically redirect to HTTPS.

## Project Structure

- `app.py` - Main Flask application with SSL support
- `insecure_routes.py` - Routes demonstrating vulnerabilities (HTTP)
- `secure_routes.py` - Secure implementation (HTTPS enforced)
- `middleware.py` - HTTPS enforcement middleware
- `database.py` - Database setup and models
- `encryption.py` - Encryption utilities (weak & strong)
- `generate_cert.sh` - SSL certificate generation script
- `ssl/` - SSL certificates directory (generated)
- `templates/` - HTML templates
- `static/` - CSS styling

## Usage

1. **Registration**: Create accounts using both insecure and secure endpoints
   - Insecure: Uses HTTP, stores passwords in plain text
   - Secure: Enforces HTTPS, hashes passwords with bcrypt
2. **Login**: Test authentication with both implementations
   - Insecure: Vulnerable to SQL injection, uses HTTP
   - Secure: Protected from SQL injection, enforces HTTPS
3. **Compare**: View side-by-side comparison of database contents
4. **Inspect**: Check the database files to see how data is stored

### Testing HTTPS Enforcement

1. Try accessing `http://localhost:5000/secure/login` (HTTP)
2. You should be automatically redirected to `https://localhost:5000/secure/login` (HTTPS)
3. This demonstrates how secure routes enforce encrypted connections

### Testing HTTP Vulnerability

1. Access `http://localhost:5000/insecure/login` (HTTP)
2. Notice the warning about insecure transmission
3. All data sent over this connection is in plain text

## Educational Purpose

This project is designed for educational purposes to demonstrate common security vulnerabilities and their proper solutions. **DO NOT use the insecure implementation in production!**

