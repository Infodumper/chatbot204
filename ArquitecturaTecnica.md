# Arquitectura Técnica del Proyecto Bot204

Este documento detalla la división de tecnologías y responsabilidades entre el **Backend** y el **Frontend** del sistema de chatbot de ventas.

---

## 🐍 Backend (Python)

El backend está desarrollado completamente en Python y su función principal es proveer la API REST, procesar la lógica de negocio, autenticación y Procesamiento de Lenguaje Natural (NLP). Es el encargado de interactuar de forma segura con los datos.

### Tecnologías principales

| Tecnología | Uso |
|---|---|
| **FastAPI** | Framework web para levantar el servidor y exponer los endpoints REST. Incluye Swagger UI automático en `/docs`. |
| **Pandas** | Motor de análisis y manipulación de datos. Lee archivos `.csv`, aplica filtros, agrupaciones y cálculos en memoria. |
| **Google Gemini API** | Modelo de lenguaje utilizado exclusivamente para la redacción final de las respuestas, partiendo del dato calculado por Pandas. |
| **NLTK** | Tokenización, limpieza y análisis del texto ingresado por el usuario. |
| **hashlib (SHA-256)** | Hashing de contraseñas para el sistema de autenticación. |

### Estructura del Backend (`/backend/`)

| Archivo | Responsabilidad |
|---|---|
| `main.py` | Servidor FastAPI. Define las rutas de la API, integra auth, NLP y Gemini. Sirve el frontend como archivos estáticos. |
| `auth.py` | Módulo de autenticación. Gestiona usuarios, hashing de contraseñas y sesiones con tokens Bearer en memoria. |
| `chat.py` | Motor NLP central. Limpia, autocorrige (Levenshtein), categoriza intenciones (Bag of Words) y resuelve consultas con Pandas. |
| `gemini_service.py` | Servicio que toma el dato calculado por Pandas y utiliza Gemini para redactar una respuesta amigable. El LLM no realiza cálculos. |
| `data_loader.py` | Funciones centralizadas para cargar los DataFrames desde los CSVs limpios. Punto único de acceso a los datos. |
| `data_processor.py` | Limpieza, transformación y estandarización de datos crudos (desde `/datos_originales` hacia `/datos_limpios`). |

### Restricciones de Arquitectura
- **Prohibido usar bases de datos** (SQLite, PostgreSQL, etc.). Toda la lectura se hace desde CSVs con Pandas.
- **El LLM no calcula.** Gemini solo redacta. Los números, filtros y agrupaciones son responsabilidad exclusiva de Pandas.
- **Sesiones en memoria.** No se persisten tokens entre reinicios del servidor.

---

## 🎨 Frontend (HTML + CSS + JS)

El frontend es una Single Page Application (SPA) ligera que se comunica de manera asíncrona con el backend mediante `fetch`.

### Tecnologías principales

| Tecnología | Uso |
|---|---|
| **HTML5** | Estructura de la interfaz: login, sidebar, chat, formularios. |
| **CSS3 (Vanilla)** | Estética siguiendo la paleta Kaizuna. Soporte completo para temas claro y oscuro con variables CSS. |
| **JavaScript (Vanilla)** | Interactividad: login, gestión de tokens en `localStorage`, envío de mensajes, manejo del DOM. |
| **Phosphor Icons** | Iconografía de la barra lateral (cargada desde CDN). |

### Estructura del Frontend (`/frontend/`)

| Archivo | Responsabilidad |
|---|---|
| `index.html` | Vista única de la aplicación. Contiene el modal de login, la barra lateral con íconos, el panel de consultas y la ventana de chat. |
| `style.css` | Estilos visuales completos. Define variables CSS para temas (claro/oscuro), animaciones, tipografías, colores Kaizuna y diseño responsive. |
| `script.js` | Controlador del lado del cliente. Maneja el ciclo de vida de la sesión (login/logout), envío de mensajes al backend, renderizado de respuestas y gestión de temas. |
| `logo/` | Directorio con el logotipo del proyecto. |

### Paleta de Colores Kaizuna

| Color | Código | Uso |
|---|---|---|
| Azul | `#145890` | Color primario, títulos, sidebar oscuro |
| Verde | `#5A8259` | Mensajes del usuario, acentos secundarios |
| Oro | `#D6A77A` | Highlights, bordes activos |

---

## 🔄 Flujo de Datos Completo

```
[Usuario escribe mensaje]
        ↓
   script.js → POST /api/chat (con token Bearer)
        ↓
   main.py → Valida token → Llama a chat.py
        ↓
   chat.py → Pipeline NLP:
     1. Limpiar + Tokenizar (NLTK)
     2. Autocorregir (Levenshtein)
     3. Categorizar intención (Bag of Words)
     4. Consultar datos (Pandas → datos_limpios/*.csv)
     5. Generar "Dato Duro"
        ↓
   gemini_service.py → Redacta respuesta amigable con Gemini
        ↓
   main.py → Devuelve JSON {reply: "..."}
        ↓
   script.js → Renderiza burbuja de respuesta en el chat
```

---

*Nota: Existe una interfaz alternativa en `streamlit_app.py` que actúa como wrapper: levanta FastAPI en un hilo secundario y lo incrusta via iframe. La interfaz principal y oficial es la SPA en HTML/CSS/JS.*
