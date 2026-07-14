# Bot204 — Chatbot de Ventas

Chatbot inteligente para consultar datos de un sistema de ventas.  
Desarrollado con **Python + Pandas** para procesamiento, la librería oficial **google-genai** (gemini-3.5-flash) para la generación de lenguaje, y una interfaz web propia (HTML/CSS/JS) como SPA principal.

**Limitaciones del Bot:**
El agente adopta el rol de **Asistente de información comercial** (tono directo y educado).
**Filtro estricto:** Solo tiene permitido responder a preguntas sobre ventas y clientes cargados, basándose enteramente en lo que el motor interno de NLP/Pandas le envía.

---

## Arquitectura del Proyecto

```
bot204/
├── backend/
│   ├── auth.py            # Autenticación SHA-256 y sesiones en memoria
│   ├── chat.py            # Motor NLP (Levenshtein, Bag of Words, NLTK)
│   ├── gemini_service.py  # Integración LLM (redacción amigable, sin cálculos)
│   ├── data_loader.py     # Carga centralizada de DataFrames
│   ├── data_processor.py  # Limpieza y transformación de CSVs
│   └── main.py            # API REST (FastAPI), auth y servidor
├── frontend/
│   ├── index.html         # Interfaz del chatbot (SPA con login)
│   ├── script.js          # Lógica del chat, login y sesión
│   ├── style.css          # Estilos Kaizuna (temas claro/oscuro)
│   └── logo/              # Logotipo del proyecto
├── datos_originales/      # CSVs crudos (NO se modifican)
├── datos_limpios/         # CSVs procesados por Pandas
├── ManualUsuario.md       # Documentación de lógicas internas y uso
├── ArquitecturaTecnica.md # División Backend / Frontend
├── requirements.txt       # Dependencias Python
├── streamlit_app.py       # Wrapper Streamlit (lanza FastAPI internamente)
└── README.md              # (este archivo)
```

---

## Requisitos Previos

- Python 3.9+
- pip

## Instalación

```bash
# 1. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
# Copiar .env.example a .env y completar con tu API Key de Gemini
copy .env.example .env
```

## Configuración

El archivo `.env` debe contener:

```
GEMINI_API_KEY=tu_api_key_de_google_gemini
GEMINI_MODEL=gemini-3.5-flash
```

> Si no se configura la API Key, el bot funciona igualmente pero devuelve los datos crudos sin redacción amigable.

## Ejecución

```bash
# Paso 1 (solo la primera vez): Procesar los datos crudos
python backend\data_processor.py

# Paso 2: Ejecutar la aplicación
streamlit run streamlit_app.py
```

Una vez levantado:
- **App principal:** [http://localhost:8501](http://localhost:8501)
- **Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

### Credenciales de Acceso

| Usuario   | Rol   | Contraseña  |
|-----------|-------|-------------|
| Ignacio   | Admin | Admin123    |
| Nacho     | User  | Usuario123  |

---

## Tecnologías Utilizadas

| Componente | Tecnología |
|---|---|
| Backend / API | Python, FastAPI |
| Autenticación | SHA-256 + sesiones Bearer en memoria |
| Procesamiento de datos | Pandas |
| Generación de texto | Google Gemini API (google-genai, gemini-3.5-flash) |
| NLP (intenciones) | NLTK, Levenshtein (propio), Bag of Words |
| Frontend | HTML5, CSS3, JavaScript (Vanilla) |
| Iconos | Phosphor Icons |
| Paleta de colores | Kaizuna (#145890, #5A8259, #D6A77A) |
