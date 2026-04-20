import sqlite3
import os

db_paths = ['backend/instance/app.db', 'instance/app.db']

for db_path in db_paths:
    if not os.path.exists(db_path):
        continue

    print(f"\n--- Database: {db_path} ---")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"Tables: {tables}")

        for table in tables:
            cursor.execute(f"SELECT count(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"Table '{table}' has {count} rows")
        
        conn.close()
    except Exception as e:
        print(f"Error checking {db_path}: {e}")
