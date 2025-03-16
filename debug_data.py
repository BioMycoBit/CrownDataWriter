from neurosity import NeurositySDK
from dotenv import load_dotenv
import os
import time
import json
from datetime import datetime

def debug_neurosity_data():
    """
    Debug script to examine what raw data looks like from the Neurosity Crown
    """
    # Load environment variables
    load_dotenv()
    
    # Initialize Neurosity SDK
    neurosity = NeurositySDK({
        "device_id": os.getenv("NEUROSITY_DEVICE_ID"),
    })
    
    # Login to Neurosity
    try:
        neurosity.login({
            "email": os.getenv("NEUROSITY_EMAIL"),
            "password": os.getenv("NEUROSITY_PASSWORD")
        })
        print("Successfully logged in")
    except Exception as e:
        print(f"Login failed: {e}")
        return
    
    # Detailed callback to inspect data structure
    def detailed_callback(data):
        print("\n----- RECEIVED DATA STRUCTURE -----")
        
        # Check if timestamp exists and format
        has_timestamp = 'timestamp' in data
        print(f"Has timestamp field: {has_timestamp}")
        if has_timestamp:
            print(f"Timestamp value: {data['timestamp']}")
            # Check timestamp format
            try:
                datetime.fromisoformat(data['timestamp'])
                print("Timestamp format: Valid ISO format")
            except ValueError:
                print("Timestamp format: Not ISO format")
        
        # Check for data field
        if 'data' in data:
            channel_count = len(data['data'])
            print(f"Channel count: {channel_count}")
            if channel_count > 0:
                # Show sample from first channel
                print(f"First channel sample (first 5 values): {data['data'][0][:5]}")
        
        # Print all keys in the data object
        print(f"All data keys: {list(data.keys())}")
        
        # Save a sample to file
        with open("neurosity_data_sample.json", "w") as f:
            json.dump(data, f, indent=2)
            print("Saved sample to neurosity_data_sample.json")
    
    # Subscribe to raw brainwaves
    unsubscribe = neurosity.brainwaves_raw(detailed_callback)
    
    try:
        print("Listening for raw brainwave data...")
        print("Press Ctrl+C to stop")
        
        # Keep script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        # Unsubscribe
        unsubscribe()
        print("Debug session ended")

if __name__ == "__main__":
    debug_neurosity_data()
