import streamlit as st
import threading
import time
import requests

st.set_page_config(layout="wide", page_title="Bot204 - Ventas", page_icon="🛍️")

# Iniciar backend FastAPI en segundo plano si no está corriendo
def run_fastapi():
    try:
        requests.get("http://127.0.0.1:8000/api/estado", timeout=1)
    except:
        import uvicorn
        from backend.main import app
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

if "fastapi_thread" not in st.session_state:
    thread = threading.Thread(target=run_fastapi, daemon=True)
    thread.start()
    st.session_state.fastapi_thread = thread
    
    # Esperamos hasta que el backend esté listo (máximo 10 segundos)
    for _ in range(10):
        try:
            if requests.get("http://127.0.0.1:8000/api/estado", timeout=1).status_code == 200:
                break
        except:
            time.sleep(1)

# Estilo para ocultar toda la UI de Streamlit y hacer el iframe verdaderamente full screen
st.markdown("""
<style>
    header[data-testid="stHeader"] { display: none !important; }
    .stDeployButton, footer { display: none !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; margin: 0 !important; }
    .stApp { overflow: hidden !important; }
    iframe { border: none; width: 100vw; height: 100vh; position: fixed; top: 0; left: 0; z-index: 9999; }
</style>
""", unsafe_allow_html=True)

# Incrustar la interfaz HTML nativa
st.markdown(f'<iframe src="http://127.0.0.1:8000/?v={{time.time()}}"></iframe>', unsafe_allow_html=True)
