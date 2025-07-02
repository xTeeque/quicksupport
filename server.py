import os
import redis
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

redis_host = os.environ.get("REDIS_HOST")
redis_port = int(os.environ.get("REDIS_PORT", 6380))
redis_password = os.environ.get("REDIS_PASSWORD")

print("REDIS_HOST:", redis_host)
print("REDIS_PORT:", redis_port)
print("REDIS_PASSWORD:", repr(redis_password))

r = redis.Redis(
    host=redis_host,
    port=redis_port,
    username="default",
    password=redis_password,
    ssl=True
)

@app.route("/generate", methods=["POST"])
def generate():
    code = "test123"  # דוגמה
    r.setex(code, 600, "some_agent")
    return jsonify({"code": code})

if __name__ == "__main__":
    app.run()
