# Bot204 — Chatbot de Ventas

Chatbot inteligente para consultar datos de un sistema de ventas.  
Desarrollado con **Python + Pandas** para procesamiento, la librería oficial **google-genai** (gemini-3.5-flash) para la generación de lenguaje, y **Streamlit** como la interfaz de usuario principal (requerimiento de la API).

**Limitaciones del Bot:**
El agente adopta el rol de **Director de Ventas** (tono directo y educado).
**Filtro estricto:** Solo tiene permitido responder a preguntas sobre ventas y clientes cargados, basándose enteramente en lo que el motor interno de NLP/Pandas le envía.

## Arquitectura del Proyecto

```
bot204/
├── backend/
│   ├── chat.py            # Motor NLP (Levenshtein, Bag of Words, NLTK)
│   ├── gemini_service.py  # Integración LLM (redacción amigable, sin cálculos)
│   ├── data_loader.py     # Carga centralizada de DataFrames
│   ├── data_processor.py  # Limpieza y transformación de CSVs
│   └── main.py            # API REST (FastAPI) y servidor
├── frontend/
│   ├── index.html         # Interfaz del chatbot
│   ├── script.js          # Lógica del chat (fetch a la API)
│   └── style.css          # Estilos Kaizuna
├── datos_originales/      # CSVs crudos (NO se modifican)
├── datos_limpios/         # CSVs procesados por Pandas
├── ManualUsuario.md       # Documentación de lógicas y uso
├── plan_chatbot.md        # Arquitectura técnica detallada
├── requirements.txt       # Dependencias Python
├── streamlit_app.py       # Interfaz alternativa en Streamlit
└── README.md              # (este archivo)
```

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
```

## Ejecución

```bash
# Paso 1: Procesar los datos (genera datos_limpios/)
python backend\data_processor.py

# Paso 2: Ejecutar la aplicación principal (Streamlit)
streamlit run streamlit_app.py

# (Opcional) Levantar API FastAPI de respaldo
uvicorn backend.main:app --reload
```

Una vez levantado Streamlit:
- **App de Ventas:** [http://localhost:8501](http://localhost:8501)

## Tecnologías Utilizadas

| Componente | Tecnología |
|---|---|
| Backend / API | Python, FastAPI |
| Procesamiento de datos | Pandas |
| Generación de texto | Google Gemini API (google-genai, gemini-3.5-flash) |
| NLP (intenciones) | NLTK, Levenshtein (propio), Bag of Words |
| Frontend | HTML5, CSS3, JavaScript |
| Paleta de colores | Kaizuna (#145890, #5A8259, #D6A77A) |
# bot204
