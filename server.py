# server.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random
import string

# Load environment variables (.env in dev, App Service in prod)
load_dotenv()

app = Flask(__name__)
# Enable CORS for your static site origin
CORS(app, resources={r"/*": {"origins": "https://quicksupport.z39.web.core.windows.net"}})

# Configuration
db_url = os.getenv('DATABASE_URL')
if not db_url:
    raise RuntimeError('DATABASE_URL environment variable is not set')
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Model and helper
def generate_unique_code(length=6):
    """Generate a unique numeric code."""
    while True:
        code = ''.join(random.choices(string.digits, k=length))
        if not Code.query.get(code):
            return code

class Code(db.Model):
    __tablename__ = 'Codes'
    code = db.Column(db.String(6), primary_key=True)
    agent_name = db.Column(db.Unicode(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

@app.before_first_request
def init_db():
    db.create_all()

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json(force=True)
    name = data.get('name')
    if not name:
        return jsonify({'error': 'missing name'}), 400
    code = generate_unique_code()
    now = datetime.utcnow()
    entry = Code(code=code, agent_name=name, created_at=now)
    db.session.add(entry)
    db.session.commit()
    return jsonify({'code': code}), 200

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json(force=True)
    code = data.get('code')
    if not code:
        return jsonify({'error': 'missing code'}), 400
    expiry = datetime.utcnow() - timedelta(minutes=10)
    Code.query.filter(Code.created_at < expiry).delete()
    db.session.commit()
    rec = Code.query.get(code)
    if rec:
        return jsonify({'status': 'match', 'agent': rec.agent_name}), 200
    return jsonify({'status': 'error'}), 404

if __name__ == '__main__':
    app.run(debug=True)
