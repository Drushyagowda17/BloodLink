import sqlite3
import os

db_path = 'instance/bloodlink.db'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Delete all data from tables
    tables = ['users', 'hospitals', 'blood_usage']
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
            print(f"Deleted all data from {table}")
        except sqlite3.Error as e:
            print(f"Error deleting from {table}: {e}")
    
    conn.commit()
    conn.close()
    print("Database emptied successfully!")
else:
    print("Database file not found.")