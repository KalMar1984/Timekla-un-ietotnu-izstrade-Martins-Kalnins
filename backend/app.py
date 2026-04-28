import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from storage import FileStorage
from datetime import datetime
import jwt
import json
from functools import wraps
from dotenv import load_dotenv

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super-secret-key')
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    entries = db.relationship('DailyEntry', backref='user', lazy=True)
    reflections = db.relationship('Refleksija', backref='user', lazy=True)

class DailyEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    positive_things = db.Column(db.JSON)
    negative_things = db.Column(db.JSON)
    gratitude = db.Column(db.JSON)
    emotions = db.Column(db.JSON)
    notes = db.Column(db.Text)
    diary_entry = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class Refleksija(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    datums = db.Column(db.String(20), nullable=False)
    sajutas = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}}, supports_credentials=True)
    
# Saknes maršruts, lai pārlūkā rādītu, ka serveris darbojas
@app.route("/")
def home():
    return "Serveris darbojas!"

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
            current_user = User.query.get(data['user_id'])
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
        
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 400
    
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password_hash=password_hash)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User created successfully', 'user_id': new_user.id}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password_hash, password):
        token = jwt.encode({'user_id': user.id}, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({'token': token, 'username': username})
    
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/entries', methods=['GET'])
@token_required
def get_entries(current_user):
    entries = DailyEntry.query.filter_by(user_id=current_user.id).order_by(DailyEntry.date.desc()).all()
    result = []
    for entry in entries:
        result.append({
            'id': entry.date,
            'date': entry.date,
            'positive_things': entry.positive_things,
            'negative_things': entry.negative_things,
            'gratitude': entry.gratitude,
            'emotions': entry.emotions,
            'notes': entry.notes,
            'diary_entry': entry.diary_entry,
            'updated_at': entry.updated_at.isoformat()
        })
    return jsonify(result)

@app.route('/api/entries', methods=['POST'])
@token_required
def create_or_update_entry(current_user):
    data = request.get_json()
    date_str = data.get('date')
    if not date_str:
        return jsonify({'message': 'Date is required'}), 400
    
    entry = DailyEntry.query.filter_by(user_id=current_user.id, date=date_str).first()
    
    if entry:
        entry.positive_things = data.get('positive_things', [])
        entry.negative_things = data.get('negative_things', [])
        entry.gratitude = data.get('gratitude', [])
        entry.emotions = data.get('emotions', [])
        entry.notes = data.get('notes', "")
        entry.diary_entry = data.get('diary_entry', "")
        entry.updated_at = datetime.utcnow()
    else:
        entry = DailyEntry(
            user_id=current_user.id,
            date=date_str,
            positive_things=data.get('positive_things', []),
            negative_things=data.get('negative_things', []),
            gratitude=data.get('gratitude', []),
            emotions=data.get('emotions', []),
            notes=data.get('notes', ""),
            diary_entry=data.get('diary_entry', ""),
            updated_at=datetime.utcnow()
        )
        db.session.add(entry)
    
    db.session.commit()
    return jsonify({'message': 'Entry saved successfully'}), 200

@app.route('/api/recommendations', methods=['GET'])
@token_required
def get_recommendations(current_user):
    entries = DailyEntry.query.filter_by(user_id=current_user.id).order_by(DailyEntry.date.desc()).limit(7).all()
    
    all_emotions = []
    total_positives = 0
    for e in entries:
        if e.emotions:
            all_emotions.extend(e.emotions)
        if e.positive_things:
            total_positives += len(e.positive_things)
    
    recommendations = []
    
    if all_emotions.count('noguris') >= 3:
        recommendations.append({'type': 'atpūta', 'message': 'Tu pēdējā laikā bieži jūties noguris. Ieteicams šodien atvēlēt laiku kārtīgai atpūtai.'})
    
    if all_emotions.count('noraizējies') >= 3:
        recommendations.append({'type': 'relaksācija', 'message': 'Pamanījām, ka esi noraizējies. Mēģini 5 minūšu elpošanas vingrinājumus vai relaksējošu vannu.'})
    
    if len(entries) > 0 and (total_positives / len(entries)) < 2:
        recommendations.append({'type': 'pozitīvais', 'message': 'Centies šodien pamanīt pat vismazākos pozitīvos mirkļus. Tas palīdzēs uzlabot omu!'})
    
    if not recommendations:
        recommendations.append({'type': 'vispārīgs', 'message': 'Turpini iesākto! Pašrefleksija ir ceļš uz labsajūtu.'})
        
    return jsonify(recommendations)

@app.route('/api/entries/<string:entry_id>', methods=['DELETE'])
@token_required
def delete_entry(current_user, entry_id):
    entry = DailyEntry.query.filter_by(user_id=current_user.id, date=entry_id).first()
    if not entry:
        return jsonify({'message': 'Entry not found'}), 404
    
    db.session.delete(entry)
    db.session.commit()
    return jsonify({'message': 'Entry deleted successfully'}), 200

# --- Refleksija Endpoints ---
@app.route('/api/refleksija', methods=['GET'])
@token_required
def get_reflections(current_user):
    reflections = Refleksija.query.filter_by(user_id=current_user.id).order_by(Refleksija.datums.desc()).all()
    result = []
    for r in reflections:
        result.append({
            'id': r.id,
            'datums': r.datums,
            'sajutas': r.sajutas,
            'updated_at': r.updated_at.isoformat()
        })
    return jsonify(result)

@app.route('/api/refleksija', methods=['POST'])
@token_required
def save_reflection(current_user):
    data = request.get_json()
    datums = data.get('datums', datetime.utcnow().strftime('%Y-%m-%d'))
    sajutas = data.get('sajutas')
    
    if not sajutas:
        return jsonify({'message': 'Sajūtas ir obligātas'}), 400
        
    new_reflection = Refleksija(
        user_id=current_user.id,
        datums=datums,
        sajutas=sajutas
    )
    db.session.add(new_reflection)
    db.session.commit()
    
    return jsonify({'message': 'Refleksija saglabāta', 'id': new_reflection.id}), 201

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
