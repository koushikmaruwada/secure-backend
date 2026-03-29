from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from crypto import encrypt_data, decrypt_data
from ml_model import analyze_query, privacy_score
from blockchain import Blockchain

app = Flask(__name__)
CORS(app)

blockchain = Blockchain()

# Dummy database
DATABASE = {
    "user1": "Medical Data A",
    "user2": "Financial Data B"
}

# USERS
USERS = {
    "admin": "1234"
}

# ------------------ QUERY ------------------
@app.route("/query", methods=["POST"])
def query():
    data = request.json
    query_text = data.get("query")

    # AI analysis (optional use)
    intent = analyze_query(query_text)

    result = DATABASE.get(query_text, "No Data Found")

    # Blockchain logging
    blockchain.add_block({
        "query": query_text,
        "result": result
    })

    return jsonify({
        "data": result,
        "privacy_score": privacy_score(query_text),
        "risk": "LOW" if privacy_score(query_text) > 80 else "MEDIUM"
    })

# ------------------ LOGIN ------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if USERS.get(username) == password:
        return jsonify({"status": "success"})

    return jsonify({"status": "fail"}), 401

# ------------------ LOGS ------------------
@app.route("/logs", methods=["GET"])
def get_logs():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            "index": block.index,
            "data": block.data,
            "hash": block.hash
        })
    return jsonify(chain_data)

# ------------------ ROOT (optional but useful) ------------------
@app.route("/", methods=["GET"])
def home():
    return "🚀 Secure AI Backend Running"

# ------------------ RUN (FIXED FOR RENDER) ------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)