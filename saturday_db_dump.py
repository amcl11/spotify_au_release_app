import pandas as pd
from datetime import datetime, timedelta
from functions import load_json_to_dataframe
import sqlite3
import logging

# Setup logging
logging.basicConfig(filename='saturday_db_update_log.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')


conn = None  # Initialize conn to None before the try block

try:
    # Attempt to read in Friday's main CSV file

    try:
        # read in Friday's main CSV file 
        df = pd.read_csv('streamlist.csv')
    except FileNotFoundError as fnf_error:
        logging.error(f"CSV file not found: {fnf_error}")
        raise  # Re-raise exception after logging to ensure script stops if file is missing


    # Add Date to CSV file before storing in SQLite 
    # As this script will run on Saturday, date needs to be one day prior
    todays_date = datetime.today()
    date_to_add = todays_date - timedelta(days=1)
    formatted_date = date_to_add.strftime('%Y-%m-%d') # Format the date as a string in 'YYYY-MM-DD' format
    df.insert(0, 'Date', formatted_date)

    # The path to the JSON file
    json_file_path = 'cover_art_data.json'

    # Call the function with the JSON file path to create the second DataFrame
    cover_info_df = load_json_to_dataframe(json_file_path)

    # Append same date as above to the second DF
    cover_info_df.insert(0, 'Date', formatted_date)

    # Combined both DFs on 'Date' and 'Playlist'
    merged_df = pd.merge(df, cover_info_df, on=['Date', 'Playlist'], how='left')

    # Save CSV file ready for SQLite dump with dynamic date in file name
    file_name = f'archived_nmf_data/{formatted_date}.csv'
    merged_df.to_csv(file_name, index=False)

    # Attempt to connect to the SQLite database
    try:
        conn = sqlite3.connect('spotify_nmf_data.db')
    except sqlite3.Error as sql_error:
        logging.error(f"Database connection failed: {sql_error}")
        raise  # Re-raise exception after logging to ensure script stops if connection fails


    # Append the DataFrame to the 'nmf_spotify_coverage' table in the database
    # The table exists, so the new data will be appended to it
    merged_df.to_sql('nmf_spotify_coverage', conn, if_exists='append', index=False)

    # Close the database connection
    conn.close()
    logging.info("Data appended to SQLite database successfully.")
    
except Exception as e:
    logging.error(f"Error occurred: {e}")
    
finally:
    # Ensure the database connection is closed in case of error
    if 'conn' in locals():
        conn.close()
        logging.info("Database connection closed.")