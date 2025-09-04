#!/usr/bin/env python3
"""
Database reset script for BloodLink.
This will completely recreate the database with all new columns.
"""

import os
import sqlite3
from datetime import datetime

def reset_database():
    """Completely reset and recreate the database."""
    
    db_path = 'bloodlink.db'
    
    # Remove existing database file if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    
    # Create new database with all tables
    print("Creating new database with updated schema...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create users table with all new columns
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                age INTEGER NOT NULL,
                gender VARCHAR(50) NOT NULL,
                blood_group VARCHAR(5) NOT NULL,
                city VARCHAR(100) NOT NULL,
                state VARCHAR(100) NOT NULL,
                pincode VARCHAR(10) NOT NULL,
                contact_number VARCHAR(15) NOT NULL,
                diseases TEXT,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(128) NOT NULL,
                role VARCHAR(20) DEFAULT 'user',
                test_hospital_name VARCHAR(200),
                blood_report_filename VARCHAR(255),
                report_status VARCHAR(20) DEFAULT 'pending',
                report_submitted_at DATETIME,
                approved_by_hospital_id INTEGER,
                is_verified_donor BOOLEAN DEFAULT 0,
                FOREIGN KEY (approved_by_hospital_id) REFERENCES hospitals (id)
            )
        ''')
        print("✓ Created users table")
        
        # Create hospitals table
        cursor.execute('''
            CREATE TABLE hospitals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                hospital_code VARCHAR(50) UNIQUE NOT NULL,
                city VARCHAR(100) NOT NULL,
                state VARCHAR(100) NOT NULL,
                contact_number VARCHAR(15) NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(128) NOT NULL,
                role VARCHAR(20) DEFAULT 'hospital'
            )
        ''')
        print("✓ Created hospitals table")
        
        # Create blood_usage table
        cursor.execute('''
            CREATE TABLE blood_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                donor_id INTEGER NOT NULL,
                hospital_id INTEGER NOT NULL,
                date DATETIME DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (donor_id) REFERENCES users (id),
                FOREIGN KEY (hospital_id) REFERENCES hospitals (id)
            )
        ''')
        print("✓ Created blood_usage table")
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX idx_users_email ON users(email)')
        cursor.execute('CREATE INDEX idx_users_blood_group ON users(blood_group)')
        cursor.execute('CREATE INDEX idx_users_city ON users(city)')
        cursor.execute('CREATE INDEX idx_users_role ON users(role)')
        cursor.execute('CREATE INDEX idx_hospitals_email ON hospitals(email)')
        cursor.execute('CREATE INDEX idx_hospitals_code ON hospitals(hospital_code)')
        print("✓ Created database indexes")
        
        # Commit changes
        conn.commit()
        print("✓ Database created successfully!")
        
        # Show table structure
        print("\nDatabase schema:")
        cursor.execute("PRAGMA table_info(users)")
        users_columns = cursor.fetchall()
        print("\nUsers table columns:")
        for col in users_columns:
            print(f"  {col[1]} ({col[2]})")
        
        cursor.execute("PRAGMA table_info(hospitals)")
        hospitals_columns = cursor.fetchall()
        print("\nHospitals table columns:")
        for col in hospitals_columns:
            print(f"  {col[1]} ({col[2]})")
        
        cursor.execute("PRAGMA table_info(blood_usage)")
        usage_columns = cursor.fetchall()
        print("\nBlood usage table columns:")
        for col in usage_columns:
            print(f"  {col[1]} ({col[2]})")
        
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    print("BloodLink Database Reset Tool")
    print("=" * 40)
    print("This will completely recreate the database with the new schema.")
    print("All existing data will be lost!")
    print()
    
    response = input("Are you sure you want to continue? (yes/no): ").lower().strip()
    
    if response in ['yes', 'y']:
        if reset_database():
            print("\n" + "=" * 40)
            print("✓ Database reset completed successfully!")
            print("You can now start your BloodLink application.")
        else:
            print("\n" + "=" * 40)
            print("✗ Database reset failed!")
    else:
        print("Database reset cancelled.")