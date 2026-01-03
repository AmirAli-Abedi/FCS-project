#!/usr/bin/env python3
"""
Generate self-signed SSL certificate using Python cryptography library
Simple version without IP addresses
"""
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime
import os


def generate_certificate():
    """Generate SSL certificate using Python cryptography"""
    print("Generating self-signed SSL certificate...")
    print("This certificate is for LOCAL DEVELOPMENT ONLY")
    print()

    # Create ssl directory if it doesn't exist
    os.makedirs("ssl", exist_ok=True)

    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Create certificate
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Organization"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ]
    )

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName(
                [
                    x509.DNSName("localhost"),
                    x509.DNSName("*.localhost"),
                ]
            ),
            critical=False,
        )
        .sign(private_key, hashes.SHA256())
    )

    # Write private key
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    with open("ssl/key.pem", "wb") as f:
        f.write(private_key_pem)

    # Write certificate
    cert_pem = cert.public_bytes(serialization.Encoding.PEM)

    with open("ssl/cert.pem", "wb") as f:
        f.write(cert_pem)

    print("Certificate generated successfully!")
    print("Files created:")
    print("  - ssl/cert.pem (certificate)")
    print("  - ssl/key.pem (private key)")
    print()
    print("Note: Browsers will show a security warning for self-signed certificates.")
    print(
        "This is expected for local development. Click 'Advanced' and 'Proceed' to continue."
    )

    return True


if __name__ == "__main__":
    generate_certificate()
