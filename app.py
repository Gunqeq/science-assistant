from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json

import google.genai as genai
from config import GEMINI_API_KEY

# ----------------------
# App Config
# ----------------------
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///science_assistant.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ----------------------
# Gemini Config
# ----------------------
client = genai.Client(api_key=GEMINI_API_KEY)

# ----------------------
# Database Model
# ----------------------
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255))
    category = db.Column(db.String(100))
    file_path = db.Column(db.String(500))
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    download_count = db.Column(db.Integer, default=0)

# ----------------------
# Load FAQ
# ----------------------
FAQ_PATH = "knowledge/faq.json"

if os.path.exists(FAQ_PATH) and os.stat(FAQ_PATH).st_size > 0:
    with open(FAQ_PATH, "r", encoding="utf-8") as f:
        FAQ_DATA = json.load(f)
else:
    FAQ_DATA = []

# ----------------------
# Routes
# ----------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/downloads")
def downloads():
    """Show downloads page with documents grouped by category"""
    documents = Document.query.order_by(Document.category).all()
    
    # Group documents by category
    categories_dict = {}
    for doc in documents:
        category = doc.category or "อื่นๆ"
        if category not in categories_dict:
            categories_dict[category] = []
        categories_dict[category].append(doc)
    
    return render_template("downloads.html", categories=categories_dict, documents=documents)

# ----------------------
# Download PDF (from static/pdfs)
# ----------------------
@app.route("/download/<filename>")
def download_pdf(filename):
    pdf_dir = os.path.join(os.path.dirname(__file__), 'static', 'pdfs')
    
    # Security: prevent directory traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        return "Invalid filename", 400
    
    file_path = os.path.join(pdf_dir, filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        return "File not found", 404
    
    return send_from_directory(pdf_dir, filename, as_attachment=True)

@app.route("/download/<int:doc_id>")
def download_file(doc_id):
    doc = Document.query.get_or_404(doc_id)

    doc.download_count += 1
    db.session.commit()

    return send_from_directory(
        os.path.dirname(doc.file_path),
        os.path.basename(doc.file_path),
        as_attachment=True,
        download_name=doc.original_filename
    )

# ----------------------
# API Routes
# ----------------------
@app.route("/api/documents")
def api_documents():
    """Get documents from static/pdfs folder with category detection"""
    pdf_dir = os.path.join(os.path.dirname(__file__), 'static', 'pdfs')
    documents = []
    
    # PDF categorization mapping
    categories = {
        'ทั่วไป': ['คำร้องทั่วไป', 'ขอลาพักการศึกษา', 'ขอรักษาสถานภาพ', 'ขอคืนสภาพนิสิต', 'ใบลา', 'คำสั่งแต่งตั้ง'],
        'ลงทะเบียน': ['ขอลงทะเบียน', 'ขอกลับเข้าศึกษา', 'KU', 'ลงทะเบียน', 'Admission'],
        'การเงิน': ['ขอผ่อนผัน', 'ขอลาออก', 'ขอคืน', 'Refund', 'Insurance', 'tuition'],
        'สอบ': ['ขอสอบชดใช้', 'แนวปฏิบัติ', 'make-up', 'exam'],
        'เอกสาร': ['รับรอง', 'Certificate', 'รายวิชา'],
        'แบบฟอร์ม': ['format', 'Form'],
    }
    
    def get_category(filename):
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword.lower() in filename.lower():
                    return category
        return 'เอกสารอื่นๆ'
    
    if os.path.exists(pdf_dir):
        for filename in sorted(os.listdir(pdf_dir)):
            if filename.endswith('.pdf'):
                documents.append({
                    'id': len(documents) + 1,
                    'name': filename,
                    'category': get_category(filename)
                })
    
    return jsonify(documents)


@app.route("/api/documents/search", methods=["POST"])
def search_documents():
    """Search documents by keyword"""
    keyword = request.json.get("keyword", "").lower()

    results = Document.query.filter(
        Document.original_filename.ilike(f"%{keyword}%")
        | Document.category.ilike(f"%{keyword}%")
    ).all()

    return jsonify([
        {
            "id": d.id,
            "name": d.original_filename,
            "category": d.category
        } for d in results
    ])

# ----------------------
# Chat API (FAQ + Gemini)
# ----------------------
@app.route("/api/chat", methods=["POST"])
def chat_api():
    user_message = request.json.get("message", "").lower()

    # FAQ matching first
    for item in FAQ_DATA:
        for kw in item["keywords"]:
            if kw in user_message:
                return jsonify({"response": item["answer"]})

    # Gemini fallback
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=f"""
คุณคือผู้ช่วยของคณะวิทยาศาสตร์ ศรีราชา มหาวิทยาลัยเกษตรศาสตร์
ตอบคำถามอย่างสุภาพ กระชับ และเป็นทางการ

คำถาม: {user_message}
"""
    )

    return jsonify({"response": response.text})

# ----------------------
# Admin Login (Simple)
# ----------------------
@app.route("/admin")
def admin_login():
    return render_template("admin_login.html")

@app.route("/admin/login", methods=["POST"])
def admin_auth():
    if request.form["username"] == "admin" and request.form["password"] == "1234":
        return redirect(url_for("dashboard"))
    return "Login failed"

# ----------------------
# Dashboard
# ----------------------
@app.route("/dashboard")
def dashboard():
    documents = Document.query.all()
    total_downloads = sum(doc.download_count for doc in documents)

    return render_template(
        "dashboard.html",
        documents=documents,
        total_downloads=total_downloads
    )

# ----------------------
# Init DB
# ----------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
