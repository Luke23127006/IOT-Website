import os, re, yaml
from typing import Dict, List, Optional
from dotenv import load_dotenv
from ..models.mq2_data import get_latest_point

# Optional: LLM fallback
try:
    from langchain_openai import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage
    USE_LLM = True
except ImportError:
    USE_LLM = False

load_dotenv()

# --------- Load YAML ---------
def load_nlu(path: str) -> Dict[str, List[str]]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    intents = {}
    for item in data.get("nlu", []):
        intent = item["intent"]
        examples = [line[2:].strip() for line in item["examples"].splitlines() if line.strip().startswith("- ")]
        intents[intent] = examples
    return intents

def load_responses(path: str) -> Dict[str, List[Dict]]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("responses", {})

# --------- Simple match ---------
def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower().strip())

def score(example: str, text: str) -> float:
    ex_tokens = set(normalize(example).split())
    tx_tokens = set(normalize(text).split())
    if not ex_tokens:
        return 0
    return len(ex_tokens & tx_tokens) / len(ex_tokens)

def match_intent(user_text: str, intents: Dict[str, List[str]], threshold: float = 0.4) -> Optional[str]:
    best_intent, best_score = None, 0
    for intent, examples in intents.items():
        for ex in examples:
            sc = score(ex, user_text)
            if sc > best_score:
                best_intent, best_score = intent, sc
    return best_intent if best_score >= threshold else None

# --------- Response ----------
def get_response(intent: Optional[str], responses: Dict[str, List[Dict]]) -> Optional[str]:
    if not intent:
        return None
    key = f"utter_{intent}"
    if key in responses:
        return responses[key][0]["text"]
    return None

# --------- Emergency guardrail ---------
EMERGENCY_PATTERNS = [
    r"\brò\s*rỉ\b", r"\bmùi\s*gas\b", r"\bcòi\b", r"\bkhẩn\s*cấp\b"
]
EMERGENCY_RESPONSE = (
    "⚠️ **An toàn trước tiên**:\n"
    "1) Mở cửa/thoáng khí;\n"
    "2) **Không** bật/tắt điện, không dùng lửa;\n"
    "3) Rời khỏi khu vực;\n"
    "4) Gọi **114**."
)

def is_emergency(text: str) -> bool:
    return any(re.search(p, text.lower()) for p in EMERGENCY_PATTERNS)

# --------- LLM fallback ---------
def llm_fallback(user_text: str) -> str:
    if not USE_LLM:
        return "Mình chưa hiểu ý bạn."
    llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0.2)
    return llm.invoke([SystemMessage(content="Bạn là trợ lý an toàn cho hệ thống gas"), HumanMessage(content=user_text)]).content

# --------- Chatbot API ---------
def chatbot_reply(user_text: str) -> str:
    if is_emergency(user_text):
        return EMERGENCY_RESPONSE
    intents = load_nlu("app/services/nlu.yml")
    responses = load_responses("app/services/domain.yml")
    
    intent = match_intent(user_text, intents)
    resp = get_response(intent, responses)
    print(f"Usertext: {user_text} Detected intent: {intent}, response: {resp}")
    if intent == "device_status":
        print("Fetching device status...")
        ppm_val = get_latest_point().get("ppm")
        return f"Nồng độ khí gas hiện tại: {ppm_val} ppm." if ppm_val is not None else "Không tìm thấy thông tin thiết bị."
    elif intent == "predict":
        #dự đoán
        pass
    if resp:
        return resp
    return "Mình chưa hiểu ý bạn. Bạn có thể thử hỏi lại hoặc mô tả rõ hơn nhé."

# --------- CLI test ---------
# if __name__ == "__main__":
#     while True:
#         msg = input("Bạn: ")
#         if msg.lower() in ["exit", "quit"]:
#             break
        
#         print("Bot:", chatbot_reply(msg))
