import sqlite3
import os

db_paths = ['backend/instance/app.db', 'instance/app.db']

for db_path in db_paths:
    if not os.path.exists(db_path):
        print(f"\n--- Database {db_path} not found ---")
        continue

    print(f"\n--- Checking {db_path} ---")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables in database:", [t[0] for t in tables])

        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT count(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"Table {table_name} has {count} rows")
            
            if count > 0:
                # Peak at data
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()
                print(f"  Sample rows: {rows}")
        
        conn.close()
    except Exception as e:
        print(f"Error checking {db_path}: {e}")
