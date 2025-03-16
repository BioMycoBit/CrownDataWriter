from neurosity import NeurositySDK
from dotenv import load_dotenv
import os
import json
import time
import threading
import sqlite3
import pandas as pd
from datetime import datetime

class NeurosityApp:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Ask for user name
        self.user_name = self._get_user_name()
        print(f"Welcome, {self.user_name}!")
        
        # Initialize Neurosity SDK
        self.neurosity = NeurositySDK({
            "device_id": os.getenv("NEUROSITY_DEVICE_ID"),
        })
        
        # Login to Neurosity
        self.login()
        
        # Initialize data buffer
        self.buffer = []
        self.buffer_size = int(os.getenv("BUFFER_SIZE", 10))
        self.buffer_flush_interval = int(os.getenv("BUFFER_FLUSH_INTERVAL", 5))
        
        # Initialize database connection
        self.db_path = os.getenv("DB_PATH", "neurosity_data.db")
        self.init_database()
        
        # Start buffer flush timer
        self.start_flush_timer()
        
        print("Neurosity app initialized")
    
    def _get_user_name(self):
        """Ask for the user's name"""
        # First check if it's in the environment variables
        user_name = os.getenv("USER_NAME")
        
        if not user_name:
            # Ask user for their name
            user_name = input("Please enter your name: ").strip()
            
            # If still empty, use a default
            if not user_name:
                user_name = "Anonymous"
                
        return user_name
    
    def login(self):
        """Login to Neurosity using credentials from .env"""
        try:
            self.neurosity.login({
                "email": os.getenv("NEUROSITY_EMAIL"),
                "password": os.getenv("NEUROSITY_PASSWORD")
            })
            print("Successfully logged in")
        except Exception as e:
            print(f"Login failed: {e}")
            exit(1)
    
    def init_database(self):
        """Initialize SQLite database and create table if not exists"""
        try:
            # Create database directory if it doesn't exist
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
            
            # Connect to SQLite database (will be created if it doesn't exist)
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            
            # Enable foreign keys
            self.conn.execute("PRAGMA foreign_keys = ON")
            
            # Create table if not exists
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS brainwaves_raw (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    data TEXT,
                    user_name TEXT
                );
            """)
            
            # Create index on timestamp
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON brainwaves_raw (timestamp);
            """)
            
            self.conn.commit()
            print(f"Database initialized at {self.db_path}")
            
        except Exception as e:
            print(f"Database initialization failed: {e}")
            exit(1)
    
    def buffer_data(self, data):
        """Add data to buffer and flush if buffer is full"""
        # We're now storing the raw data object directly since we already added a timestamp
        # in the brainwave_callback function if it was missing
        
        # Add to buffer
        self.buffer.append(data)
        
        # Check if buffer is full
        if len(self.buffer) >= self.buffer_size:
            self.flush_buffer()
    
    def flush_buffer(self):
        """Write buffered data to database"""
        if not self.buffer:
            return
        
        try:
            cursor = self.conn.cursor()
            
            # Insert all buffered data
            for item in self.buffer:
                # Get timestamp from the data or use current time
                timestamp = item.get('timestamp', datetime.now().isoformat())
                
                cursor.execute(
                    "INSERT INTO brainwaves_raw (timestamp, data, user_name) VALUES (?, ?, ?)",
                    (
                        timestamp,
                        json.dumps(item),
                        self.user_name
                    )
                )
            
            self.conn.commit()
            print(f"Flushed {len(self.buffer)} records to database")
            
            # Clear buffer
            self.buffer = []
            
        except Exception as e:
            print(f"Error writing to database: {e}")
    
    def start_flush_timer(self):
        """Start a timer to flush the buffer periodically"""
        def flush_timer():
            while True:
                time.sleep(self.buffer_flush_interval)
                if self.buffer:
                    print(f"Timer triggered flush of {len(self.buffer)} records")
                    self.flush_buffer()
        
        # Start timer in a separate thread
        timer_thread = threading.Thread(target=flush_timer, daemon=True)
        timer_thread.start()
    
    def brainwave_callback(self, data):
        """Callback function for brainwave data"""
        # Add our own timestamp if one doesn't exist in the data
        if not data.get('timestamp'):
            data['timestamp'] = datetime.now().isoformat()
        
        # Print data summary
        channels = len(data.get('data', []))
        print(f"Received data: {channels} channels, timestamp: {data.get('timestamp')}")
        
        # Buffer the data
        self.buffer_data(data)
    
    def start(self):
        """Start listening to brainwaves"""
        print("Starting to listen for brainwaves...")
        self.unsubscribe = self.neurosity.brainwaves_raw(self.brainwave_callback)
    
    def stop(self):
        """Stop listening and close connection"""
        if hasattr(self, 'unsubscribe'):
            self.unsubscribe()
        
        # Flush remaining data
        self.flush_buffer()
        
        # Close database connection
        if hasattr(self, 'conn'):
            self.conn.close()
        
        print("Application stopped")

    def query_data(self, limit=10):
        """Query the most recent data from the database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT timestamp, data, user_name FROM brainwaves_raw
            ORDER BY timestamp DESC LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        for timestamp, data, user_name in results:
            print(f"Timestamp: {timestamp}, User: {user_name}")
            # Print a summary of the data
            data_obj = json.loads(data)
            print(f"  Channels: {len(data_obj.get('data', []))}")
            print(f"  Device ID: {data_obj.get('deviceId', 'unknown')}")
            print("-" * 40)
        
        return results

# Main execution
if __name__ == "__main__":
    app = NeurosityApp()
    
    try:
        app.start()
        # Keep the main thread running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping application...")
        app.stop()
    except Exception as e:
        print(f"Error: {e}")
        app.stop()
