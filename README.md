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

## Running the Application

```bash
python app.py
```

Then open your browser and navigate to: `http://localhost:5000`

## Project Structure

- `app.py` - Main Flask application
- `insecure_routes.py` - Routes demonstrating vulnerabilities
- `secure_routes.py` - Secure implementation
- `database.py` - Database setup and models
- `encryption.py` - Encryption utilities (weak & strong)
- `templates/` - HTML templates
- `static/` - CSS styling

## Usage

1. **Registration**: Create accounts using both insecure and secure endpoints
2. **Login**: Test authentication with both implementations
3. **Compare**: View side-by-side comparison of database contents
4. **Inspect**: Check the database files to see how data is stored

## Educational Purpose

This project is designed for educational purposes to demonstrate common security vulnerabilities and their proper solutions. **DO NOT use the insecure implementation in production!**

