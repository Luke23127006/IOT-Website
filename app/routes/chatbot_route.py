# app/routes/chatbot_route.py
from flask import Blueprint, request, jsonify
from ..services.chatbot_service import chatbot_reply
from pathlib import Path
import json

chatbot_bp = Blueprint("chatbot", __name__, url_prefix="/api")

CHAT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "chat_data.json"

def read_chat_data():
    if CHAT_DATA_PATH.exists():
        with open(CHAT_DATA_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"history": []}

def write_chat_data(data):
    with open(CHAT_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@chatbot_bp.route("/chatbot", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_text = (data.get("message") or "").strip()
    if not user_text:
        return jsonify({"error": "message is required"}), 400
    
    reply = chatbot_reply(user_text)

    chat_data = read_chat_data()
    chat_data["history"].append({"role": "user", "text": user_text})
    chat_data["history"].append({"role": "bot", "text": reply})
    write_chat_data(chat_data)

    return jsonify({"reply": reply})

@chatbot_bp.route("/chatbot/history", methods=["GET"])
def chat_history():
    chat_data = read_chat_data()
    if chat_data == {"history": []}:
        chat_data["history"].append({
            "role": "bot",
            "text": "Xin chào! 👋. Tôi là trợ lý ảo của bạn. Tôi có thể giúp gì cho bạn hôm nay? Bạn có thể hỏi về tình trạng cảm biến, hướng dẫn lắp đặt, hoặc các vấn đề liên quan đến khí gas."
        })
        write_chat_data(chat_data)
    
    return jsonify(chat_data)