import sqlite3
import json
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
import numpy as np
from datetime import datetime, timedelta

class NeurosityDataViewer:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get database path from environment variable
        self.db_path = os.getenv("DB_PATH", "neurosity_data.db")
        
        # Connect to SQLite database
        self.conn = sqlite3.connect(self.db_path)
        
        # Check if database exists and has data
        self._check_database()
    
    def _check_database(self):
        """Check if the database exists and has data"""
        cursor = self.conn.cursor()
        
        # Check if brainwaves_raw table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='brainwaves_raw'
        """)
        
        if not cursor.fetchone():
            print(f"Database at {self.db_path} does not contain brainwaves_raw table")
            return False
        
        # Check if there's any data
        cursor.execute("SELECT COUNT(*) FROM brainwaves_raw")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("No data found in database")
            return False
        
        print(f"Database contains {count} records")
        return True
    
    def get_recent_data(self, limit=10):
        """Get the most recent data from the database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT timestamp, data, user_name FROM brainwaves_raw
            ORDER BY timestamp DESC LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        print(f"Retrieved {len(results)} recent records")
        
        # Convert to pandas DataFrame
        records = []
        for timestamp, data_str, user_name in results:
            data = json.loads(data_str)
            record = {
                'timestamp': timestamp,
                'user_name': user_name,
                'channels': len(data.get('data', [])),
                'deviceId': data.get('deviceId', 'unknown')
            }
            records.append(record)
        
        return pd.DataFrame(records)
    
    def get_data_by_timerange(self, start_time, end_time):
        """Get data within a specific time range"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT timestamp, data FROM brainwaves_raw
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp
        """, (start_time, end_time))
        
        results = cursor.fetchall()
        print(f"Retrieved {len(results)} records between {start_time} and {end_time}")
        
        return results
    
    def plot_data_volume_by_hour(self, days=1):
        """Plot the volume of data collected by hour for the last n days"""
        # Calculate the start time
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                substr(timestamp, 1, 13) as hour, 
                COUNT(*) as count,
                user_name
            FROM brainwaves_raw
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY hour, user_name
            ORDER BY hour
        """, (start_time.isoformat(), end_time.isoformat()))
        
        results = cursor.fetchall()
        
        if not results:
            print("No data available for the specified time range")
            return
        
        # Convert to pandas DataFrame
        df = pd.DataFrame(results, columns=['hour', 'count', 'user_name'])
        
        # Plot
        plt.figure(figsize=(12, 6))
        plt.bar(df['hour'], df['count'])
        plt.title('Data Volume by Hour')
        plt.xlabel('Hour')
        plt.ylabel('Number of Records')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    
    def export_to_csv(self, output_file, limit=None):
        """Export data to CSV file"""
        cursor = self.conn.cursor()
        
        if limit:
            cursor.execute("""
                SELECT id, timestamp, data, user_name FROM brainwaves_raw
                ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
        else:
            cursor.execute("""
                SELECT id, timestamp, data, user_name FROM brainwaves_raw
                ORDER BY timestamp DESC
            """)
        
        results = cursor.fetchall()
        print(f"Exporting {len(results)} records to {output_file}")
        
        # Convert to pandas DataFrame
        records = []
        for id, timestamp, data_str, user_name in results:
            data = json.loads(data_str)
            # Extract basic metadata from data
            record = {
                'id': id,
                'timestamp': timestamp,
                'user_name': user_name,
                'deviceId': data.get('deviceId', 'unknown'),
                'data_json': data_str  # Include full JSON for reference
            }
            records.append(record)
        
        df = pd.DataFrame(records)
        df.to_csv(output_file, index=False)
        print(f"Data exported to {output_file}")
    
    def close(self):
        """Close the database connection"""
        self.conn.close()
        print("Database connection closed")

# Usage example
if __name__ == "__main__":
    viewer = NeurosityDataViewer()
    
    try:
        # Get recent data
        recent_data = viewer.get_recent_data(limit=5)
        print(recent_data)
        
        # Plot data volume by hour for the last day
        viewer.plot_data_volume_by_hour(days=1)
        
        # Export data to CSV
        viewer.export_to_csv("neurosity_export.csv", limit=100)
    finally:
        viewer.close()
