#!/usr/bin/env python3
"""
Database migration script to add new columns to existing BloodLink database.
Run this script to update your database schema with the new donor verification features.
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Add new columns to the users table for donor verification features."""
    
    db_path = 'bloodlink.db'
    
    if not os.path.exists(db_path):
        print("Database file not found. Creating new database...")
        return
    
    print("Starting database migration...")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the new columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        new_columns = [
            'test_hospital_name',
            'blood_report_filename', 
            'report_status',
            'report_submitted_at',
            'approved_by_hospital_id',
            'is_verified_donor'
        ]
        
        # Add missing columns
        for column in new_columns:
            if column not in columns:
                print(f"Adding column: {column}")
                
                if column == 'test_hospital_name':
                    cursor.execute("ALTER TABLE users ADD COLUMN test_hospital_name VARCHAR(200)")
                elif column == 'blood_report_filename':
                    cursor.execute("ALTER TABLE users ADD COLUMN blood_report_filename VARCHAR(255)")
                elif column == 'report_status':
                    cursor.execute("ALTER TABLE users ADD COLUMN report_status VARCHAR(20) DEFAULT 'pending'")
                elif column == 'report_submitted_at':
                    cursor.execute("ALTER TABLE users ADD COLUMN report_submitted_at DATETIME")
                elif column == 'approved_by_hospital_id':
                    cursor.execute("ALTER TABLE users ADD COLUMN approved_by_hospital_id INTEGER")
                elif column == 'is_verified_donor':
                    cursor.execute("ALTER TABLE users ADD COLUMN is_verified_donor BOOLEAN DEFAULT 0")
            else:
                print(f"Column {column} already exists, skipping...")
        
        # Update existing users to have default values
        print("Updating existing users with default values...")
        cursor.execute("""
            UPDATE users 
            SET report_status = 'pending', 
                is_verified_donor = 0 
            WHERE report_status IS NULL OR is_verified_donor IS NULL
        """)
        
        # Commit changes
        conn.commit()
        print("Database migration completed successfully!")
        
        # Show updated table structure
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("\nUpdated table structure:")
        for column in columns:
            print(f"  {column[1]} ({column[2]})")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if conn:
            conn.close()
    
    return True

def backup_database():
    """Create a backup of the current database before migration."""
    db_path = 'bloodlink.db'
    if os.path.exists(db_path):
        backup_path = f'bloodlink_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"Database backed up to: {backup_path}")
        return backup_path
    return None

if __name__ == '__main__':
    print("BloodLink Database Migration Tool")
    print("=" * 40)
    
    # Create backup
    backup_file = backup_database()
    if backup_file:
        print(f"✓ Backup created: {backup_file}")
    
    # Run migration
    if migrate_database():
        print("✓ Migration completed successfully!")
        print("\nYou can now restart your BloodLink application.")
    else:
        print("✗ Migration failed!")
        if backup_file:
            print(f"You can restore from backup: {backup_file}")