# Bot204 — Chatbot de Ventas

Chatbot inteligente para consultar datos de un sistema de ventas.  
Desarrollado con **Python + FastAPI + Pandas** (backend) y **HTML/CSS/JS** (frontend).

## Arquitectura del Proyecto

```
chatbot_gmn/
├── backend/
│   ├── chat.py            # Motor NLP (Levenshtein, Bag of Words, NLTK)
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

# Paso 2: Levantar el servidor
uvicorn backend.main:app --reload
```

Una vez levantado:
- **Chatbot:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Tecnologías Utilizadas

| Componente | Tecnología |
|---|---|
| Backend / API | Python, FastAPI |
| Procesamiento de datos | Pandas |
| NLP (intenciones) | NLTK, Levenshtein (propio), Bag of Words |
| Frontend | HTML5, CSS3, JavaScript |
| Paleta de colores | Kaizuna (#145890, #5A8259, #D6A77A) |
