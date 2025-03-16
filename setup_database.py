import sqlite3
from dotenv import load_dotenv
import os

def setup_database():
    """
    Set up the SQLite database for the Neurosity app
    """
    # Load environment variables
    load_dotenv()
    
    # Get database path from environment variable
    db_path = os.getenv("DB_PATH", "neurosity_data.db")
    
    # Create database directory if it doesn't exist
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # Connect to SQLite database (will be created if it doesn't exist)
    conn = sqlite3.connect(db_path)
    
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Create tables
    cursor = conn.cursor()
    
    # Create brainwaves_raw table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS brainwaves_raw (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            data TEXT,
            user_name TEXT
        );
    """)
    
    # Create index on timestamp for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp ON brainwaves_raw (timestamp);
    """)
    
    # Create a table for aggregated data (for analysis)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS aggregated_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_timestamp TEXT,
            end_timestamp TEXT,
            avg_values TEXT,
            record_count INTEGER,
            info TEXT
        );
    """)
    
    conn.commit()
    print(f"Database set up successfully at {db_path}")
    
    # Close connection
    cursor.close()
    conn.close()

def query_database():
    """
    Query the database to check if it's working properly
    """
    # Load environment variables
    load_dotenv()
    
    # Get database path from environment variable
    db_path = os.getenv("DB_PATH", "neurosity_data.db")
    
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get number of records
    cursor.execute("SELECT COUNT(*) FROM brainwaves_raw")
    count = cursor.fetchone()[0]
    print(f"Database contains {count} records")
    
    # Get most recent record
    if count > 0:
        cursor.execute("""
            SELECT timestamp, data FROM brainwaves_raw
            ORDER BY timestamp DESC LIMIT 1
        """)
        timestamp, data = cursor.fetchone()
        print(f"Most recent record: {timestamp}")
    
    # Close connection
    cursor.close()
    conn.close()

if __name__ == "__main__":
    setup_database()
    query_database()
