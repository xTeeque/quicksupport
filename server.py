# server.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random
import string

# Load environment variables from .env (local) or from App Service settings (prod)
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Database model
def generate_unique_code(length=6):
    """Generate a unique 6-digit code not already in the database."""
    while True:
        c = ''.join(random.choices(string.digits, k=length))
        if not Code.query.get(c):
            return c

class Code(db.Model):
    __tablename__ = 'Codes'
    code       = db.Column(db.String(6), primary_key=True)
    agent_name = db.Column(db.Unicode(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

@app.before_first_request
def create_tables():
    # Create tables if they don't exist
    db.create_all()

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    agent_name = data.get('name')
    if not agent_name:
        return jsonify({'error': 'missing name'}), 400

    code = generate_unique_code()
    now = datetime.utcnow()
    new_code = Code(code=code, agent_name=agent_name, created_at=now)
    db.session.add(new_code)
    db.session.commit()
    return jsonify({'code': code})

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    code = data.get('code')
    if not code:
        return jsonify({'error': 'missing code'}), 400

    # Remove expired codes (older than 10 minutes)
    expiry = datetime.utcnow() - timedelta(minutes=10)
    Code.query.filter(Code.created_at < expiry).delete()
    db.session.commit()

    record = Code.query.get(code)
    if record:
        return jsonify({'status': 'match', 'agent': record.agent_name})
    return jsonify({'status': 'error'})

if __name__ == '__main__':
    app.run(debug=True)
