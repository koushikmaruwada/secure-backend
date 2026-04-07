from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pandas as pd

from db import add_block, get_blocks
from crypto import encrypt_data, decrypt_data
from ml_model import privacy_score

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

# 🔐 Encrypted Database (in-memory)
DATABASE = {}

# USERS
USERS = {
    "admin": "1234"
}

# ------------------ HOME ------------------
@app.route("/", methods=["GET"])
def home():
    return "🚀 Secure AI Backend Running"

# ------------------ FILE UPLOAD ------------------
@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]

    data_dict = {}

    # Excel / CSV
    if file.filename.endswith(".xlsx") or file.filename.endswith(".csv"):
        df = pd.read_excel(file) if file.filename.endswith(".xlsx") else pd.read_csv(file)

    df = df.fillna("")

    for index, row in df.iterrows():
        # 🔥 combine ALL columns
        combined_data = " | ".join([str(v).strip() for v in row.values])

        # use index as key (unique)
        key = f"row_{index}"

        DATABASE[key] = encrypt_data(combined_data)

# ------------------ QUERY ------------------
@app.route("/query", methods=["POST"])
def query():
    data = request.json
    query_text = data.get("query").lower().strip()

    results = []

    for key, encrypted_data in DATABASE.items():
        decrypted_data = decrypt_data(encrypted_data)

        if query_text in decrypted_data.lower():
            results.append(decrypted_data)

    if results:
        add_block({
            "query": query_text,
            "result": "MATCH FOUND"
        })
    else:
        results = ["No Data Found"]
        add_block({
            "query": query_text,
            "result": "NOT FOUND"
        })

    return jsonify({
        "data": results,
        "privacy_score": 90,
        "risk": "LOW"
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
def logs():
    return jsonify(get_blocks())

# ------------------ RUN ------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)