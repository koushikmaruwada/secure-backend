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

        for index, row in df.iterrows():
            key = str(row[0])
            value = " | ".join([str(v) for v in row[1:]])

            data_dict[key] = encrypt_data(value)

    # TXT
    elif file.filename.endswith(".txt"):
        lines = file.read().decode("utf-8").split("\n")

        for line in lines:
            parts = line.split(",")
            if len(parts) >= 2:
                key = parts[0]
                value = ",".join(parts[1:])
                data_dict[key] = encrypt_data(value)

    DATABASE.update(data_dict)

    return jsonify({"status": "File uploaded & encrypted"})

# ------------------ QUERY ------------------
@app.route("/query", methods=["POST"])
def query():
    data = request.json
    query_text = data.get("query")

    if query_text in DATABASE:
        encrypted_data = DATABASE[query_text]
        decrypted_result = decrypt_data(encrypted_data)

        add_block({
            "query": query_text,
            "result": decrypted_result
        })
    else:
        decrypted_result = "No Data Found"

        add_block({
            "query": query_text,
            "result": "NOT FOUND"
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

# ------------------ LOGS ------------------
@app.route("/logs", methods=["GET"])
def logs():
    return jsonify(get_blocks())

# ------------------ RUN ------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)