from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from crypto import encrypt_data, decrypt_data
from ml_model import analyze_query, privacy_score
from blockchain import Blockchain

# ------------------ APP SETUP ------------------
app = Flask(__name__)

# ✅ CORS FIX (important for Vercel → Render communication)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

# ------------------ INIT ------------------
blockchain = Blockchain()

# Dummy database
DATABASE = {
    "patient_101": encrypt_data("Name: John, Disease: Diabetes"),
    "account_202": encrypt_data("Balance: ₹50,000")
}

# USERS
USERS = {
    "admin": "1234"
}

# ------------------ HOME ------------------
@app.route("/", methods=["GET"])
def home():
    return "🚀 Secure AI Backend Running"

# ------------------ QUERY ------------------
@app.route("/query", methods=["POST"])
def query():
    data = request.json
    query_text = data.get("query")

    # 🔐 Check if data exists (NO full decryption)
    if query_text in DATABASE:
        encrypted_data = DATABASE[query_text]

        # 🔓 Decrypt ONLY required data
        decrypted_result = decrypt_data(encrypted_data)
    else:
        decrypted_result = "No Data Found"

    # Blockchain logging
    blockchain.add_block({
        "query": query_text,
        "result": "DECRYPTED" if query_text in DATABASE else "NOT FOUND"
    })

    score = privacy_score(query_text)

    return jsonify({
        "data": decrypted_result,
        "privacy_score": score,
        "risk": "LOW" if score > 80 else "MEDIUM"
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

# ------------------ BLOCKCHAIN LOGS ------------------
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

# ------------------ RUN (RENDER FIX) ------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

