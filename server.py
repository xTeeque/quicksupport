from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import string
import redis
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # ← חשוב!

r = redis.Redis(host='localhost', port=6379, db=0)

def generate_unique_code(length=6):
    while True:
        code = ''.join(random.choices(string.digits, k=length))
        if not r.exists(code):
            return code

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    agent_name = data.get('name')

    code = generate_unique_code()
    r.setex(code, 600, agent_name)

    return jsonify({'code': code})

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    code = data.get('code')

    agent_name = r.get(code)
    if agent_name:
        agent_name = agent_name.decode()
        return jsonify({'status': 'match', 'agent': agent_name})
    else:
        return jsonify({'status': 'error'})

if __name__ == '__main__':
    app.run(debug=True)
