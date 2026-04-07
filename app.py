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
    try:
        file = request.files["file"]
        import pandas as pd

        df = pd.read_excel(file)
        df = df.fillna("")

        # 🔥 store column names
        columns = list(df.columns)

        for index, row in df.iterrows():
            record = {}

            for col in columns:
                record[col.lower()] = str(row[col]).strip()

            # store structured + encrypted
            DATABASE[f"row_{index}"] = encrypt_data(str(record))

        return jsonify({"status": "Upload success"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------ QUERY ------------------
import ast   # 🔥 add this at TOP of file (once)

@app.route("/query", methods=["POST"])
def query():
    data = request.json
    query_text = data.get("query").lower()

    results = []

    for key, encrypted_data in DATABASE.items():
        decrypted_data = decrypt_data(encrypted_data)

        # 🔥 ADD HERE
        record = ast.literal_eval(decrypted_data)

        # 🔍 check if name matches
        if any(query_text.split()[0] in str(v).lower() for v in record.values()):

            if "attendance" in query_text:
                results.append(record.get("attendance", "Not found"))

            elif "supply" in query_text:
                results.append(record.get("supply", "Not found"))

            else:
                results.append(record)

    if not results:
        results = ["No Data Found"]

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