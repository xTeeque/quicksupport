from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import string
import redis
import time
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # ← חשוב!

import os
import redis

redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = os.environ.get("REDIS_PORT", 6379)
redis_password = os.environ.get("REDIS_PASSWORD", None)

r = redis.Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password,
    ssl=True
)

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
