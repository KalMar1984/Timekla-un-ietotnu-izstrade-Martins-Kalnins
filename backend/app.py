import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from storage import FileStorage
from datetime import datetime
import jwt
import json
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super-secret-key')

storage = FileStorage()
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}}, supports_credentials=True)

# Auth Decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = storage.get_user_by_id(data['user_id'])
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
        except Exception as e:
            print(f"Token error: {e}")
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': 'Username and password required'}), 400
        
    user_id = storage.register_user(username, password)
    if not user_id:
        return jsonify({'message': 'User already exists'}), 400
    
    return jsonify({'message': 'User created successfully', 'user_id': user_id}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user_data = storage.authenticate_user(username, password)
    if user_data:
        token = jwt.encode({'user_id': user_data['id']}, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token, 'username': username})
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/entries', methods=['GET'])
@token_required
def get_entries(current_user):
    entries = storage.get_entries(current_user['username'])
    return jsonify(entries)

@app.route('/api/entries', methods=['POST'])
@token_required
def create_or_update_entry(current_user):
    data = request.get_json()
    # Frontend sends date, positive_things, etc.
    entry = storage.save_entry(current_user['username'], data)
    if not entry:
        return jsonify({'message': 'Failed to save entry'}), 400
    return jsonify(entry), 200

@app.route('/api/recommendations', methods=['GET'])
@token_required
def get_recommendations(current_user):
    entries = storage.get_entries(current_user['username'])[:7]
    
    all_emotions = []
    total_positives = 0
    for e in entries:
        all_emotions.extend(e.get('emotions', []))
        total_positives += len(e.get('positive_things', []))
    
    recommendations = []
    
    # Ja bieži “noguris”
    if all_emotions.count('noguris') >= 3:
        recommendations.append({'type': 'atpūta', 'message': 'Tu pēdējā laikā bieži jūties noguris. Ieteicams šodien atvēlēt laiku kārtīgai atpūtai.'})
    
    # Ja bieži “noraizējies”
    if all_emotions.count('noraizējies') >= 3:
        recommendations.append({'type': 'relaksācija', 'message': 'Pamanījām, ka esi noraizējies. Mēģini 5 minūšu elpošanas vingrinājumus vai relaksējošu vannu.'})
    
    # Ja maz pozitīvo ierakstu
    if len(entries) > 0 and (total_positives / len(entries)) < 2:
        recommendations.append({'type': 'pozitīvais', 'message': 'Centies šodien pamanīt pat vismazākos pozitīvos mirkļus. Tas palīdzēs uzlabot omu!'})
    
    # Default recommendation if nothing else
    if not recommendations:
        recommendations.append({'type': 'vispārīgs', 'message': 'Turpini iesākto! Pašrefleksija ir ceļš uz labsajūtu.'})
        
    return jsonify(recommendations)

@app.route('/api/entries/<string:entry_id>', methods=['DELETE'])
@token_required
def delete_entry(current_user, entry_id):
    # For file storage, entry_id is the date
    success = storage.delete_entry(current_user['username'], entry_id)
    if not success:
        return jsonify({'message': 'Entry not found'}), 404
    
    return jsonify({'message': 'Entry deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
