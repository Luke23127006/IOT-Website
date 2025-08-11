# app/routes/chatbot_route.py
from flask import Blueprint, request, jsonify
from ..services.chatbot_service import chatbot_reply

chatbot_bp = Blueprint("chatbot", __name__, url_prefix="/api")

@chatbot_bp.route("/chatbot", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_text = (data.get("message") or "").strip()
    if not user_text:
        return jsonify({"error": "message is required"}), 400
    reply = chatbot_reply(user_text)
    return jsonify({"reply": reply})
