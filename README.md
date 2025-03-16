# Neurosity Crown Data Collector

This application collects raw brainwave data from a Neurosity Crown device, buffers it, and saves it to a SQLite database.

## Features

- Connection to Neurosity Crown device
- Data buffering to reduce database write operations
- SQLite database storage (no external database required)
- Configurable buffer size and flush interval
- Timestamp handling and data validation
- Debug tools for data inspection

## Requirements

- Python 3.8+
- Neurosity Crown device

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Copy the `.env.example` file to `.env` and update it with your credentials:

```bash
cp .env.example .env
```

3. Edit the `.env` file with your Neurosity credentials and settings.

4. Set up the database:

```bash
python setup_database.py
```

5. Run the application:

```bash
python app.py
```

## Configuration

The application can be configured via the `.env` file:

- `NEUROSITY_DEVICE_ID`: Your Crown device ID
- `NEUROSITY_EMAIL`: Your Neurosity account email
- `NEUROSITY_PASSWORD`: Your Neurosity account password
- `USER_NAME`: (Optional) Your name - if provided, will skip the name prompt
- `DB_PATH`: Path to the SQLite database file
- `BUFFER_SIZE`: Number of records to buffer before writing to the database
- `BUFFER_FLUSH_INTERVAL`: Time in seconds to wait before flushing the buffer regardless of size

## Included Scripts

The application includes several scripts:

### Main Application

- `app.py`: The main application that collects and stores data
- `setup_database.py`: Creates and initializes the SQLite database

### Utilities

- `data_viewer.py`: Provides tools to view, analyze, and export collected data
- `debug_data.py`: A debugging tool to inspect raw data from the Neurosity Crown

## How It Works

1. The app connects to your Neurosity Crown device
2. Raw brainwave data is received in real-time
3. Timestamps are added to data if they don't exist
4. Data is temporarily stored in an in-memory buffer
5. The buffer is flushed to the database when:
   - The buffer reaches the configured size
   - The flush interval timer triggers
6. Data is stored in the `brainwave_data` table with timestamp and metadata

## Data Schema

The `brainwaves_raw` table has the following structure:

- `id`: Integer primary key
- `timestamp`: Time when the data was recorded (ISO format)
- `data`: JSON text containing the raw brainwave data
- `user_name`: Name of the user who recorded the data

Additionally, there's an `aggregated_data` table that can be used for storing processed/aggregated data:

- `id`: Integer primary key
- `start_timestamp`: Start time of the aggregation period
- `end_timestamp`: End time of the aggregation period
- `avg_values`: JSON text containing averaged values
- `record_count`: Number of records included in the aggregation
- `info`: Additional information

## Debugging

If you encounter issues or want to inspect the raw data structure, you can use the included debug script:

```bash
python debug_data.py
```

This will:
- Connect to your Neurosity Crown device
- Display detailed information about the data structure
- Save a sample of raw data to `neurosity_data_sample.json`
- Show whether the data includes a timestamp field
- Display channel information and data format

## Data Analysis

You can analyze the collected data using the included data viewer utility:

```bash
python data_viewer.py
```

This provides functions to:
- View recent data records
- Plot data volume over time
- Export data to CSV for further analysis

## Querying Data

You can query the collected data by using the `query_data` method in the `NeurosityApp` class or by directly querying the SQLite database:

```python
import sqlite3

conn = sqlite3.connect('neurosity_data.db')
cursor = conn.cursor()
cursor.execute("SELECT timestamp, data FROM brainwaves_raw LIMIT 10")
for row in cursor.fetchall():
    print(row)
conn.close()
```

## Stopping the Application

Press `Ctrl+C` to gracefully stop the application. This will flush any remaining data in the buffer to the database before exiting.
