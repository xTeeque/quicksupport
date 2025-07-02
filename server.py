from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import string
import time

app = Flask(__name__)
CORS(app)

codes = {}

def generate_unique_code(length=6):
    while True:
        code = ''.join(random.choices(string.digits, k=length))
        if code not in codes:
            return code


@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    agent_name = data.get('name')
    code = generate_unique_code()
    timestamp = time.time()

    codes[code] = {'name': agent_name, 'timestamp': timestamp}
    return jsonify({'code': code})

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    code = data.get('code')

    now = time.time()
    expired_codes = [c for c, v in codes.items() if now - v['timestamp'] > 600]
    for c in expired_codes:
        del codes[c]

    if code in codes:
        agent_name = codes[code]['name']
        return jsonify({'status': 'match', 'agent': agent_name})
    else:
        return jsonify({'status': 'error'})

if __name__ == '__main__':
    app.run(debug=True)
