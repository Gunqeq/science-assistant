from flask import Flask, render_template, request, jsonify, send_from_directory
import google.generativeai as genai
import os
import re
from dotenv import load_dotenv
from prompt import prompt
from scraper import get_kusrc_data

# โหลดค่า environment จากไฟล์ .env (แต่ไม่ expose ออกไป)
load_dotenv()

def clean_response(text):
    """Clean markdown and emojis but preserve HTML formatting"""
    if not text:
        return text
    
    # ถ้ามี HTML tags ให้คืนค่าเหมือนเดิม (ไม่ต้องเอา)
    if '<' in text and '>' in text:
        return text.strip()
    
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold **text**
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic *text*
    text = re.sub(r'\*\*\*', '', text)            # Bold italic ***
    text = re.sub(r'```[\s\S]*?```', '', text)   # Code blocks
    text = re.sub(r'`(.*?)`', r'\1', text)       # Inline code
    # Remove emojis
    emoji_pattern = re.compile(
        "[" 
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642"
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"
        u"\u3030"
        "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)
    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    return text.strip()

app = Flask(__name__)

# ======================
# CONFIG (ฝั่ง server เท่านั้น)
# ======================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# เก็บ prompt และ context อย่างเดียว (ไม่มี api_key)
CHAT_SETTINGS = {
    "system_prompt": prompt,
    "context": []
}

# ======================
# โหลดข้อมูลตอน start
# ======================
try:
    print("Loading knowledge base from KUSRC...")
    CHAT_SETTINGS["context"] = get_kusrc_data()
    print(f"Loaded {len(CHAT_SETTINGS['context'])} documents.")
except Exception as e:
    print(f"Failed to load knowledge base: {e}")

# ======================
# ROUTES
# ======================
@app.route('/')
def home():
    return render_template('chat.html')


@app.route('/downloads')
def downloads():
    """Show downloads page"""
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
    
    # Group documents by category
    categories_dict = {}
    if os.path.exists(pdf_dir):
        for idx, filename in enumerate(sorted(os.listdir(pdf_dir)), 1):
            if filename.endswith('.pdf'):
                category = get_category(filename)
                if category not in categories_dict:
                    categories_dict[category] = []
                
                categories_dict[category].append({
                    'id': idx,
                    'filename': filename,
                    'original_filename': filename,
                    'upload_date': None,
                    'download_count': 0
                })
    
    return render_template('downloads.html', categories=categories_dict)


@app.route('/api/documents')
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


@app.route('/download/<int:doc_id>')
def download_file(doc_id):
    """Download PDF file by ID"""
    pdf_dir = os.path.join(os.path.dirname(__file__), 'static', 'pdfs')
    
    # Get all PDFs with their IDs
    documents = []
    if os.path.exists(pdf_dir):
        for filename in sorted(os.listdir(pdf_dir)):
            if filename.endswith('.pdf'):
                documents.append(filename)
    
    # Check if doc_id is valid
    if doc_id < 1 or doc_id > len(documents):
        return "File not found", 404
    
    filename = documents[doc_id - 1]
    return send_from_directory(pdf_dir, filename, as_attachment=True)


@app.route('/api/documents/search', methods=['POST'])
def search_documents():
    """Search documents by keyword"""
    pdf_dir = os.path.join(os.path.dirname(__file__), 'static', 'pdfs')
    keyword = request.json.get("keyword", "").lower()
    
    # Categories for document classification
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
            for keyword_item in keywords:
                if keyword_item.lower() in filename.lower():
                    return category
        return 'เอกสารอื่นๆ'
    
    results = []
    if os.path.exists(pdf_dir):
        for idx, filename in enumerate(sorted(os.listdir(pdf_dir)), 1):
            if filename.endswith('.pdf'):
                if keyword in filename.lower() or keyword in get_category(filename).lower():
                    results.append({
                        'id': idx,
                        'filename': filename,
                        'category': get_category(filename)
                    })
    
    return jsonify(results)


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        return render_template('chat.html')
    
    data = request.get_json(silent=True)
    if not data or 'message' not in data:
        return jsonify({'response': 'Invalid request'}), 400

    user_message = data.get('message', '')

    # ======================
    # ถ้ามี API KEY → ใช้ Gemini
    # ======================
    if GEMINI_API_KEY:
        try:
            # รวม context
            context_str = ""
            if CHAT_SETTINGS['context']:
                context_str += "\n\nRelevant Information:\n"
                for doc in CHAT_SETTINGS['context']:
                    context_str += (
                        f"Source: {doc['source']} ({doc['category']})\n"
                        f"Content: {doc['content'][:4000]}...\n\n"
                    )

            full_prompt = CHAT_SETTINGS['system_prompt'] + context_str

            model = genai.GenerativeModel(
                model_name='gemini-flash-latest',
                system_instruction=full_prompt
            )

            response = model.generate_content(user_message)
            bot_response = clean_response(response.text)

        except Exception as e:
            bot_response = f"AI Error: {str(e)}"

    # ======================
    # ไม่มี API KEY → ตอบแบบ fallback
    # ======================
    else:
        msg = user_message.lower()
        if 'hello' in msg or 'hi' in msg or 'สวัสดี' in msg:
            bot_response = "สวัสดีครับ มีอะไรให้ช่วยไหมครับ"
        elif 'คุณคือใคร' in msg or 'who are you' in msg:
            bot_response = "ผมคือ AI Chatbot สำหรับตอบคำถามข้อมูลคณะวิทยาศาสตร์"
        elif 'bye' in msg or 'ลาก่อน' in msg:
            bot_response = "ลาก่อนครับ ขอให้เป็นวันที่ดี"
        else:
            bot_response = "ขออภัยครับ ระบบไม่สามารถตอบคำถามนี้ได้ โปรดลองใหม่หรือติดต่อเจ้าหน้าที่"

    return jsonify({'response': bot_response})


# ======================
# RUN
# ======================
if __name__ == '__main__':
    app.run(debug=True)
