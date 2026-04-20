import os
import json
import uuid
from datetime import datetime
from flask_bcrypt import Bcrypt

class FileStorage:
    def __init__(self, data_dir=None):
        if data_dir is None:
            # Use data folder inside the same directory as storage.py
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_dir = os.path.join(base_dir, 'data')
        else:
            self.data_dir = data_dir
            
        self.entries_dir = os.path.join(self.data_dir, 'entries')
        self.users_file = os.path.join(self.data_dir, 'users.json')
        self.bcrypt = Bcrypt()
        
        # Ensure directories exist
        os.makedirs(self.entries_dir, exist_ok=True)
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)

    def _load_users(self):
        with open(self.users_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_users(self, users):
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=4, ensure_ascii=False)

    def register_user(self, username, password):
        users = self._load_users()
        if username in users:
            return None
        
        user_id = str(uuid.uuid4())
        password_hash = self.bcrypt.generate_password_hash(password).decode('utf-8')
        
        users[username] = {
            'id': user_id,
            'password_hash': password_hash,
            'created_at': datetime.utcnow().isoformat()
        }
        self._save_users(users)
        
        # Create user entry directory
        os.makedirs(os.path.join(self.entries_dir, username), exist_ok=True)
        return user_id

    def authenticate_user(self, username, password):
        users = self._load_users()
        user_data = users.get(username)
        if user_data and self.bcrypt.check_password_hash(user_data['password_hash'], password):
            return user_data
        return None

    def get_user_by_id(self, user_id):
        users = self._load_users()
        for username, data in users.items():
            if data['id'] == user_id:
                return {**data, 'username': username}
        return None

    def save_entry(self, username, entry_data):
        # entry_data should contain 'date' and other fields
        date_str = entry_data.get('date')
        if not date_str:
            return None
        
        user_dir = os.path.join(self.entries_dir, username)
        os.makedirs(user_dir, exist_ok=True)
        
        file_path = os.path.join(user_dir, f"{date_str}.json")
        
        # Clean up data for storage (ensure sync_status is set)
        entry_to_save = {
            **entry_data,
            'id': date_str, # Use date as ID for folder storage
            'updated_at': datetime.utcnow().isoformat(),
            'sync_status': 'synced'
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(entry_to_save, f, indent=4, ensure_ascii=False)
            
        return entry_to_save

    def get_entries(self, username):
        user_dir = os.path.join(self.entries_dir, username)
        if not os.path.exists(user_dir):
            return []
        
        entries = []
        for filename in os.listdir(user_dir):
            if filename.endswith('.json'):
                with open(os.path.join(user_dir, filename), 'r', encoding='utf-8') as f:
                    entries.append(json.load(f))
        
        # Sort by date descending
        entries.sort(key=lambda x: x['date'], reverse=True)
        return entries

    def delete_entry(self, username, entry_date):
        file_path = os.path.join(self.entries_dir, username, f"{entry_date}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
