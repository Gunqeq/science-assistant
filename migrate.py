"""
migrate.py — เพิ่ม column feedback ใน chat_log
รันครั้งเดียว: python migrate.py
"""
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "science_assistant.db")

conn = sqlite3.connect(DB_PATH)
cur  = conn.cursor()

# ตรวจว่ามี column นี้แล้วหรือยัง
cols = [row[1] for row in cur.execute("PRAGMA table_info(chat_log)").fetchall()]

if "feedback" not in cols:
    cur.execute("ALTER TABLE chat_log ADD COLUMN feedback INTEGER")
    conn.commit()
    print("✅ เพิ่ม column 'feedback' เรียบร้อยแล้วครับ")
else:
    print("ℹ️  มี column 'feedback' อยู่แล้ว ไม่ต้องทำอะไรครับ")

conn.close()