# Implementación de la Lógica del Chatbot

Este plan detalla cómo conectaremos el frontend visual con el backend en Python para responder preguntas sobre los datos, respetando la regla fundamental de `AGENTS.md`: **Pandas hace el trabajo pesado y el LLM (si se usa) solo redacta.**

## User Review Required

> [!IMPORTANT]
> **Uso de un Modelo de Lenguaje (LLM):** En `requirements.txt` tenemos instalada la librería de Gemini (`google-generativeai`), pero necesitamos una API Key para que funcione. 
> - ¿Tienes una API Key de Gemini (Google AI Studio) lista para colocar en un archivo `.env`?
> - ¿O prefieres que armemos un sistema inicial basado en "palabras clave" (RegEx) en Python para detectar intenciones (ej: "cumpleaños" + "mayo") sin depender de internet ni de una API Key por ahora?

## Open Questions

> [!TIP]
> ¿Qué alcance de preguntas esperas para esta primera versión del chatbot? 
> Además de los cumpleaños por mes, ¿quieres que busque clientes por líder, o cuente pedidos de una campaña en específico? He propuesto un diseño escalable para añadir más "intenciones" fácilmente.

## Proposed Changes

---

### Backend (FastAPI + Lógica)

#### [NEW] [chat.py](file:///c:/TGPN/chatbot_gmn/backend/chat.py)
Crearemos un módulo independiente para procesar los mensajes. El flujo será:
1. **Analizador de Intenciones:** Leerá el mensaje del usuario y extraerá de qué está hablando (ej: `intencion="cumpleanos_mes"`, `mes=5`).
2. **Procesador Pandas:** Se conectará a las funciones de `main.py` para obtener el DataFrame filtrado (ej: contar cuántos registros cumplen la condición).
3. **Generador de Respuesta:** Redactará una oración amable con el resultado exacto (ej: "Hay 15 clientes que cumplen años en mayo.").

#### [MODIFY] [main.py](file:///c:/TGPN/chatbot_gmn/backend/main.py)
Añadiremos un nuevo endpoint:
- `POST /api/chat`: Recibirá el texto del usuario desde el frontend, llamará a la lógica en `chat.py` y devolverá la respuesta.

---

### Frontend

#### [MODIFY] [script.js](file:///c:/TGPN/chatbot_gmn/frontend/script.js)
Actualizaremos la función que simula el chat para que haga una petición `fetch()` real a `POST /api/chat`, enviando el mensaje que escribas y mostrando la respuesta real que devuelve FastAPI.

---

## Verification Plan

### Manual Verification
- Iniciaremos el servidor.
- Abriremos el Frontend (`http://127.0.0.1:8000/`).
- Escribiremos: "¿Cuántos clientes cumplen años en el mes de mayo?"
- Verificaremos que el resultado numérico devuelto por el chatbot coincida exactamente con el filtro equivalente en el Swagger UI (`/clientes/por-mes-cumpleanos/5`).
