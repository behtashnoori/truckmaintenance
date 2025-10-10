#!/usr/bin/env python3
"""Reset admin password"""
import hashlib
import secrets
import psycopg2

def set_password(password):
    """Hash password"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex() + ':' + salt
    return password_hash

conn = psycopg2.connect(
    host='localhost',
    port='5432',
    user='postgres',
    password='bagheri13',
    database='Marketplace'
)

cursor = conn.cursor()

# Reset admin password to 'admin123'
new_password = 'admin123'
password_hash = set_password(new_password)

cursor.execute("""
    UPDATE users 
    SET password_hash = %s 
    WHERE username = 'admin'
""", (password_hash,))

conn.commit()

print("✅ Admin password reset successfully!")
print("   Username: admin")
print("   Password: admin123")

conn.close()

