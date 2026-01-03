"""
Encryption utilities demonstrating weak and strong encryption methods.
This module shows the difference between weak encoding (base64) and 
proper encryption (AES-256).
"""
import base64
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import hashlib


# Weak Encryption Functions (VULNERABLE - DO NOT USE IN PRODUCTION)

def weak_encrypt(data):
    """
    WEAK ENCRYPTION - Base64 encoding is NOT encryption!
    This is just encoding and can be easily decoded by anyone.
    VULNERABILITY: Base64 is not encryption, it's just encoding.
    Anyone can decode it without a key.
    """
    if not data:
        return ""
    return base64.b64encode(data.encode()).decode()


def weak_decrypt(encoded_data):
    """
    Decode base64 - this is trivial to reverse.
    VULNERABILITY: No security at all, just encoding.
    """
    if not encoded_data:
        return ""
    try:
        return base64.b64decode(encoded_data.encode()).decode()
    except:
        return ""


# Strong Encryption Functions (SECURE - Use in production)

# Generate a key for AES encryption
# In production, this should be stored securely (environment variable, key management service)
ENCRYPTION_KEY = os.urandom(32)  # 256-bit key for AES-256


def get_encryption_key():
    """
    Get or generate encryption key.
    In production, use a proper key management system!
    """
    return ENCRYPTION_KEY


def strong_encrypt(data):
    """
    STRONG ENCRYPTION - AES-256 encryption
    This uses proper symmetric encryption with a secret key.
    SECURE: Cannot be decrypted without the key.
    """
    if not data:
        return ""
    
    # Generate a random IV (Initialization Vector) for each encryption
    iv = os.urandom(16)
    
    # Create cipher
    cipher = Cipher(
        algorithms.AES(get_encryption_key()),
        modes.CBC(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    
    # Pad the data to block size (AES block size is 16 bytes)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data.encode())
    padded_data += padder.finalize()
    
    # Encrypt
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    # Combine IV and ciphertext, then encode to base64 for storage
    encrypted_data = iv + ciphertext
    return base64.b64encode(encrypted_data).decode()


def strong_decrypt(encrypted_data):
    """
    Decrypt AES-256 encrypted data
    SECURE: Requires the encryption key to decrypt.
    """
    if not encrypted_data:
        return ""
    
    try:
        # Decode from base64
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        
        # Extract IV (first 16 bytes) and ciphertext
        iv = encrypted_bytes[:16]
        ciphertext = encrypted_bytes[16:]
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(get_encryption_key()),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Unpad
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data)
        data += unpadder.finalize()
        
        return data.decode()
    except Exception as e:
        return f"Decryption error: {str(e)}"

