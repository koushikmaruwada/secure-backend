from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pandas as pd
import ast

from docx import Document
from PyPDF2 import PdfReader

from db import add_block, get_blocks
from crypto import encrypt_data, decrypt_data
from ml_model import privacy_score

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# 🔐 Encrypted Database
DATABASE = {}

USERS = {
    "admin": "1234"
}

# ------------------ HOME ------------------
@app.route("/", methods=["GET"])
def home():
    return "🚀 Secure AI Backend Running"

# ------------------ FILE UPLOAD ------------------
from docx import Document
from PyPDF2 import PdfReader
import pandas as pd

# 🔥 Helper: Convert text → key:value dictionary
def parse_text_to_dict(text):
    record = {}
    lines = text.split("\n")

    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            record[key.strip().lower()] = value.strip()

    return record


# ------------------ FILE UPLOAD ------------------
DATABASE.clear()
@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        DATABASE.clear()
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        filename = file.filename.lower()

        data_list = []

        # 📊 EXCEL / CSV
        if filename.endswith(".xlsx") or filename.endswith(".csv"):
            df = pd.read_excel(file) if filename.endswith(".xlsx") else pd.read_csv(file)
            df = df.fillna("")

            columns = list(df.columns)

            for _, row in df.iterrows():
                record = {}
                for col in columns:
                    record[col.lower()] = str(row[col]).strip()

                data_list.append(record)

        # 📄 TXT
        elif filename.endswith(".txt"):
            content = file.read().decode("utf-8")

            record = parse_text_to_dict(content)
            if record:
                data_list.append(record)

        # 📄 WORD (.docx)
        elif filename.endswith(".docx"):
            doc = Document(file)

            text = "\n".join([p.text for p in doc.paragraphs])

            record = parse_text_to_dict(text)
            if record:
                data_list.append(record)

        # 📄 PDF
        elif filename.endswith(".pdf"):
            reader = PdfReader(file)

            full_text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    full_text += extracted + "\n"

            record = parse_text_to_dict(full_text)
            if record:
                data_list.append(record)

        else:
            return jsonify({"error": "Unsupported file type"}), 400

        # 🔐 Encrypt & store
        for i, record in enumerate(data_list):
            DATABASE[f"row_{len(DATABASE)+i}"] = encrypt_data(str(record))

        return jsonify({
            "status": "Upload success",
            "records_added": len(data_list)
        })

    except Exception as e:
        print("UPLOAD ERROR:", str(e))
        return jsonify({"error": str(e)}), 500


# ------------------ QUERY ------------------
import ast

@app.route("/query", methods=["POST"])
def query():
    data = request.json
    query_text = data.get("query").lower().strip()

    words = query_text.split()
    results = []

    for key, encrypted_data in DATABASE.items():
        decrypted_data = decrypt_data(encrypted_data)
        record = ast.literal_eval(decrypted_data)

        # 🔍 Check if any word matches record
        if any(word in str(value).lower() for word in words for value in record.values()):

            matched_data = {}

            # 🔥 dynamic field extraction
            for field in record.keys():
                for word in words:
                    if word in field:
                        matched_data[field] = record[field]

            # if specific fields found
            if matched_data:
                results.append(matched_data)

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
    if USERS.get(data.get("username")) == data.get("password"):
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