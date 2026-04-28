import os
import json
from app import app, db, User, DailyEntry
from datetime import datetime

def migrate():
    with app.app_context():
        print("Initializing database...")
        db.create_all()
        
        # Paths
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, 'data')
        users_file = os.path.join(data_dir, 'users.json')
        entries_dir = os.path.join(data_dir, 'entries')
        
        if not os.path.exists(users_file):
            print(f"No users file found at {users_file}. Skipping migration.")
            return

        # 1. Migrate Users
        print("Migrating users...")
        with open(users_file, 'r', encoding='utf-8') as f:
            users_data = json.load(f)
        
        user_id_map = {} # Maps username to DB user ID
        
        for username, info in users_data.items():
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                # We use the existing password hash from JSON
                new_user = User(
                    username=username,
                    password_hash=info['password_hash'],
                    created_at=datetime.fromisoformat(info['created_at'])
                )
                db.session.add(new_user)
                db.session.flush() # To get the ID
                user_id_map[username] = new_user.id
                print(f"  Added user: {username}")
            else:
                user_id_map[username] = existing_user.id
                print(f"  User {username} already exists.")
        
        db.session.commit()
        
        # 2. Migrate Entries
        print("Migrating entries...")
        if os.path.exists(entries_dir):
            for username in os.listdir(entries_dir):
                user_path = os.path.join(entries_dir, username)
                if not os.path.isdir(user_path):
                    continue
                
                user_db_id = user_id_map.get(username)
                if not user_db_id:
                    print(f"  User {username} not found in DB. Skipping entries.")
                    continue
                
                print(f"  Migrating entries for {username}...")
                for entry_file in os.listdir(user_path):
                    if not entry_file.endswith('.json'):
                        continue
                    
                    with open(os.path.join(user_path, entry_file), 'r', encoding='utf-8') as f:
                        entry_data = json.load(f)
                    
                    # Check if entry already exists
                    date_str = entry_data.get('date')
                    existing_entry = DailyEntry.query.filter_by(user_id=user_db_id, date=date_str).first()
                    
                    if not existing_entry:
                        new_entry = DailyEntry(
                            user_id=user_db_id,
                            date=date_str,
                            positive_things=entry_data.get('positive_things', []),
                            negative_things=entry_data.get('negative_things', []),
                            gratitude=entry_data.get('gratitude', []),
                            emotions=entry_data.get('emotions', []),
                            notes=entry_data.get('notes', ""),
                            diary_entry=entry_data.get('diary_entry', ""),
                            updated_at=datetime.fromisoformat(entry_data['updated_at']) if 'updated_at' in entry_data else datetime.utcnow()
                        )
                        db.session.add(new_entry)
                
                db.session.commit()
                print(f"  Done with {username}.")
        
        print("\nMigration completed successfully!")

if __name__ == '__main__':
    migrate()
