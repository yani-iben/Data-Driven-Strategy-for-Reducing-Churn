import pandas as pd
from sqlalchemy import create_engine
import os

# DATABASE CONNECTION CONFIGURATION
# Format: postgresql://[username]:[password]@[host]:[port]/[database_name]
# Modify 'postgres' and 'your_password' to match your local PostgreSQL credentials
DB_URI = "postgresql+psycopg2://yani@localhost:5432/volunteer_analytics"

print("Connecting to the database engine...")
engine = create_engine(DB_URI)

# This pairs generated files with the exact target tables in PostgreSQL
data_pipeline_mapping = {
    "data/dim_chapters.csv": "dim_chapters",
    "data/dim_events.csv": "dim_events",
    "data/dim_volunteers.csv": "dim_volunteers",
    "data/fact_volunteer_activity.csv": "fact_volunteer_activity",
    "data/fact_donations.csv": "fact_donations"
}

def run_pipeline():
    print("Starting ETL Data Load Process...")
    
    # Load dimension tables first due to Foreign Key constraints
    load_order = [
        "data/dim_chapters.csv", 
        "data/dim_events.csv", 
        "data/dim_volunteers.csv", 
        "data/fact_volunteer_activity.csv", 
        "data/fact_donations.csv"
    ]
    
    for file_path in load_order:
        table_name = data_pipeline_mapping[file_path]
        
        if not os.path.exists(file_path):
            print(f"CRITICAL ERROR: File not found at {file_path}. Skipping.")
            continue
            
        print(f"Reading {file_path} into memory...")
        df = pd.read_csv(file_path)
        
        print(f"Bulk loading {len(df)} records into target table '{table_name}'...")
        
        # 'append' adds records. If you want a complete clear/refresh every run, use 'replace'
        # 'method="multi"' optimizes performance by executing batch inserts rather than row-by-row
        df.to_sql(
            name=table_name, 
            con=engine, 
            if_exists='replace', 
            index=False, 
            method='multi'
        )
        print(f"Successfully loaded '{table_name}'.")

    print("\n🎉 ETL pipeline execution completed successfully! Warehouse is fully loaded.")

if __name__ == "__main__":
    run_pipeline()