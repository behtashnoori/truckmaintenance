"""Check database tables and structure"""
import sqlite3
import os

db_path = "instance/truckmaintenance.db"

if not os.path.exists(db_path):
    print(f"ERROR: Database file not found at {db_path}")
    exit(1)

print(f"Database file: {db_path}")
print(f"File size: {os.path.getsize(db_path)} bytes")
print("\n" + "="*60)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

print(f"Total tables: {len(tables)}")
print("\nTables:")
for table in tables:
    print(f"  - {table[0]}")

# Check provider_application table
print("\n" + "="*60)
if ('provider_application',) in tables:
    print("Table 'provider_application' EXISTS")
    
    # Get table structure
    cursor.execute("PRAGMA table_info(provider_application);")
    columns = cursor.fetchall()
    print("\nColumns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Count records
    cursor.execute("SELECT COUNT(*) FROM provider_application;")
    count = cursor.fetchone()[0]
    print(f"\nTotal records: {count}")
    
    if count > 0:
        cursor.execute("SELECT id, company_name, phone_mobile, status FROM provider_application LIMIT 5;")
        records = cursor.fetchall()
        print("\nLast 5 records:")
        for rec in records:
            print(f"  ID: {rec[0]}, Company: {rec[1]}, Phone: {rec[2]}, Status: {rec[3]}")
else:
    print("ERROR: Table 'provider_application' DOES NOT EXIST")

# Check category table
print("\n" + "="*60)
if ('category',) in tables:
    print("Table 'category' EXISTS")
    cursor.execute("SELECT COUNT(*) FROM category;")
    count = cursor.fetchone()[0]
    print(f"Total categories: {count}")
else:
    print("WARNING: Table 'category' DOES NOT EXIST")

# Check provider_application_category table
print("\n" + "="*60)
if ('provider_application_category',) in tables:
    print("Table 'provider_application_category' EXISTS (many-to-many)")
else:
    print("WARNING: Table 'provider_application_category' DOES NOT EXIST")

conn.close()
print("\n" + "="*60)
print("Database check complete!")

