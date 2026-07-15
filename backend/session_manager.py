import json
import os
import uuid
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chat_history.json")

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_history(data):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving chat history: {e}")

def get_user_sessions(username: str):
    data = load_history()
    user_data = data.get(username, [])
    # Devolver lista resumida
    return [{"id": s["id"], "title": s.get("title", "Nueva Consulta"), "created_at": s.get("created_at")} for s in user_data]

def get_session_messages(username: str, session_id: str):
    data = load_history()
    user_data = data.get(username, [])
    for s in user_data:
        if s["id"] == session_id:
            return s.get("messages", [])
    return []

def create_session(username: str, initial_message=None):
    data = load_history()
    if username not in data:
        data[username] = []
        
    session_id = str(uuid.uuid4())
    num_sessions = len(data[username]) + 1
    
    new_session = {
        "id": session_id,
        "title": f"Consulta {num_sessions}",
        "created_at": datetime.now().isoformat(),
        "messages": [
            {"role": "bot", "content": "¡Hola! 👋 Soy <b>Bot204</b>, tu asistente de información comercial. ¿En qué te puedo ayudar hoy?"}
        ]
    }
    
    if initial_message:
        new_session["messages"].append(initial_message)
        
    data[username].insert(0, new_session) # Add at the beginning
    save_history(data)
    return session_id

def add_message_to_session(username: str, session_id: str, role: str, content: str):
    data = load_history()
    user_data = data.get(username, [])
    
    for s in user_data:
        if s["id"] == session_id:
            s["messages"].append({"role": role, "content": content})
            save_history(data)
            return True
            
    # Si no existe la sesión, la creamos y agregamos el mensaje
    session_id = create_session(username)
    return add_message_to_session(username, session_id, role, content)
