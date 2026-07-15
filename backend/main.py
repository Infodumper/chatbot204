"""
main.py — Servidor API REST (FastAPI) del proyecto Bot204.

Expone endpoints para:
  - Autenticación (login con tokens Bearer).
  - Consultas directas a datos de clientes, pedidos y líderes (Swagger).
  - Chat con el bot (NLP + Gemini).
  - Servir el frontend estático (SPA).

Ejecución:
    uvicorn backend.main:app --reload
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import pandas as pd
from pydantic import BaseModel

from backend.data_loader import get_clientes_df, get_pedidos_df, get_lideres_df
import backend.auth as auth
from backend.session_manager import get_user_sessions, get_session_messages, add_message_to_session, create_session

app = FastAPI(
    title="API del Chatbot Bot204",
    description="API Backend para procesar datos de ventas con Pandas y conversar con el chatbot.",
    version="2.0.0"
)

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    user = auth.get_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/login", tags=["Auth"])
def login(request: LoginRequest):
    user = auth.authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )
    token = auth.create_session(user)
    return {"access_token": token, "token_type": "bearer", "user": {"username": user["username"], "role": user["role"]}}

@app.get("/api/estado", tags=["Sistema"])
def get_estado():
    from backend.session_manager import HISTORY_FILE
    import os
    return {"estado": "online", "mensaje": "El backend y Swagger están funcionando correctamente.", "history_file": HISTORY_FILE, "exists": os.path.exists(HISTORY_FILE)}

@app.get("/clientes", tags=["Clientes"])
def get_todos_los_clientes():
    """Obtiene la lista completa de clientes."""
    df = get_clientes_df()
    return df.to_dict(orient="records")

@app.get("/clientes/por-nro/{nro}", tags=["Clientes"])
def get_clientes_por_nro(nro: float):
    """Filtra clientes por Nro exacto."""
    df = get_clientes_df()
    df = df[df['Nro'] == nro]
    return df.to_dict(orient="records")

@app.get("/clientes/por-nombre/{cliente}", tags=["Clientes"])
def get_clientes_por_nombre(cliente: str):
    """Filtra clientes por nombre (coincidencia parcial)."""
    df = get_clientes_df()
    df = df[df['Nombre'].astype(str).str.contains(cliente, case=False, na=False)]
    return df.to_dict(orient="records")

@app.get("/clientes/por-lider/{lider}", tags=["Clientes"])
def get_clientes_por_lider_alternativo(lider: float):
    """Filtra clientes por Nro del Líder."""
    df = get_clientes_df()
    df = df[df['Lider'] == lider]
    return df.to_dict(orient="records")

@app.get("/clientes/por-documento/{nro_doc}", tags=["Clientes"])
def get_clientes_por_documento(nro_doc: float):
    """Filtra clientes por Nro de Documento."""
    df = get_clientes_df()
    df = df[df['NroDoc'] == nro_doc]
    return df.to_dict(orient="records")

@app.get("/clientes/por-localidad/{localidad}", tags=["Clientes"])
def get_clientes_por_localidad(localidad: str):
    """Filtra clientes por Localidad exacta."""
    df = get_clientes_df()
    df = df[df['Localidad'].astype(str).str.upper() == localidad.upper()]
    return df.to_dict(orient="records")

@app.get("/clientes/por-email/{email}", tags=["Clientes"])
def get_clientes_por_email(email: str):
    """Filtra clientes por Email (coincidencia parcial)."""
    df = get_clientes_df()
    df = df[df['Email'].astype(str).str.contains(email, case=False, na=False)]
    return df.to_dict(orient="records")

@app.get("/clientes/por-telefono/{telefono}", tags=["Clientes"])
def get_clientes_por_telefono(telefono: str):
    """Filtra clientes por Teléfono (coincidencia parcial)."""
    df = get_clientes_df()
    df = df[df['Telefono'].astype(str).str.contains(telefono, case=False, na=False)]
    return df.to_dict(orient="records")

@app.get("/clientes/por-mes-cumpleanos/{fecnac_mes}", tags=["Clientes"])
def get_clientes_por_mes_cumpleanos(fecnac_mes: int):
    """Filtra clientes por mes de nacimiento (1 al 12)."""
    df = get_clientes_df()
    df_temp_dates = pd.to_datetime(df['FecNac'], errors='coerce')
    df = df[df_temp_dates.dt.month == fecnac_mes]
    return df.to_dict(orient="records")

@app.get("/lideres", tags=["Líderes"])
def get_lideres():
    df = get_lideres_df()
    return df.to_dict(orient="records")

@app.get("/lideres/{nro_lider}/clientes", tags=["Líderes"])
def get_clientes_de_lider(nro_lider: float):
    df = get_clientes_df()
    df = df[df['Lider'] == nro_lider]
    return df.to_dict(orient="records")

@app.get("/pedidos", tags=["Pedidos"])
def get_todos_los_pedidos():
    """Obtiene la lista completa de pedidos."""
    df = get_pedidos_df()
    return df.to_dict(orient="records")

@app.get("/pedidos/por-cliente/{nro_cliente}", tags=["Pedidos"])
def get_pedidos_por_cliente(nro_cliente: float):
    """Filtra pedidos por el Nro del cliente."""
    df = get_pedidos_df()
    df = df[df['Nro'] == nro_cliente]
    return df.to_dict(orient="records")

@app.get("/pedidos/por-lider/{nro_lider}", tags=["Pedidos"])
def get_pedidos_por_lider(nro_lider: float):
    """Filtra pedidos por el Nro del líder."""
    df = get_pedidos_df()
    df = df[df['Lider'] == nro_lider]
    return df.to_dict(orient="records")

from typing import Optional

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

@app.get("/api/chat/sessions", tags=["Chatbot"])
def get_sessions(current_user: dict = Depends(get_current_user)):
    """Obtiene el historial de sesiones del usuario actual."""
    username = current_user.get("username", "default")
    return get_user_sessions(username)

@app.get("/api/chat/sessions/{session_id}", tags=["Chatbot"])
def get_session_details(session_id: str, current_user: dict = Depends(get_current_user)):
    """Obtiene los mensajes de una sesión específica."""
    username = current_user.get("username", "default")
    return get_session_messages(username, session_id)

@app.post("/api/chat", tags=["Chatbot"])
def chat_endpoint(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """Procesa un mensaje del usuario y devuelve la respuesta del chatbot enriquecida con Gemini."""
    from backend.chat import procesar_mensaje
    from backend.gemini_service import generar_respuesta_amigable
    
    username = current_user.get("username", "default")
    session_id = request.session_id
    session_messages = get_session_messages(username, session_id) if session_id else []
    es_primer_mensaje = len(session_messages) <= 1 # <= 1 porque el primer elemento siempre es el saludo del bot
    
    if not session_id:
        session_id = create_session(username)
        
    add_message_to_session(username, session_id, "user", request.message)
    
    dato_duro = procesar_mensaje(request.message, username)
    respuesta = generar_respuesta_amigable(request.message, dato_duro, es_primer_mensaje)
    
    add_message_to_session(username, session_id, "bot", respuesta)
    
    return {"reply": respuesta, "session_id": session_id}

frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/", tags=["Frontend"], include_in_schema=False)
    def serve_frontend():
        return FileResponse(os.path.join(frontend_path, "index.html"))
