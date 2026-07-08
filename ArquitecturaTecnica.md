# Arquitectura Técnica del Proyecto Bot204

Este documento detalla la división de tecnologías y responsabilidades entre el **Backend** y el **Frontend** del sistema de chatbot de ventas.

## 🐍 Backend (Python)
El backend está desarrollado completamente en Python y su función principal es proveer la API REST y procesar la lógica de negocio y Procesamiento de Lenguaje Natural (NLP). Además, es el encargado de interactuar de forma segura con los datos.

*   **Tecnologías principales:**
    *   **FastAPI:** Framework web para levantar el servidor y exponer los endpoints REST.
    *   **Pandas:** Motor de análisis y manipulación de datos. Se utiliza para leer los archivos `.csv`, aplicar filtros, buscar información y realizar agrupaciones o cálculos (como promedios y sumas) en memoria.
    *   **NLTK (Natural Language Toolkit):** Utilizado para tokenizar, limpiar y analizar el texto ingresado por el usuario.

*   **Estructura del Backend (`/backend/`):**
    *   `main.py`: Archivo principal que levanta el servidor FastAPI, define las rutas de la API (como `/api/chat`) e integra el motor NLP.
    *   `chat.py`: Contiene toda la lógica central del chatbot (NLP). Se encarga de recibir el texto, limpiarlo, autocorregirlo (usando distancia de Levenshtein), categorizar la intención del usuario y determinar la respuesta utilizando Pandas.
    *   `data_loader.py`: Script con funciones utilitarias y centralizadas para leer en caché (usando DataFrames de Pandas) los archivos CSV que fueron previamente limpiados.
    *   `data_processor.py`: Módulo para la limpieza, transformación y estandarización de los datos crudos (desde `/datos_originales` hacia `/datos_limpios`).

---

## 🎨 Frontend (HTML + CSS + JS)
El frontend se encarga de la interfaz gráfica y la experiencia del usuario (UI/UX). Es una Single Page Application (SPA) sencilla y ligera que se comunica de manera asíncrona con el backend.

*   **Tecnologías principales:**
    *   **HTML5:** Para estructurar la interfaz del chat, definiendo los contenedores de mensajes, barra de entrada y botones.
    *   **CSS3 (Vanilla):** Para la estética y diseño visual, siguiendo los lineamientos de diseño de la marca (paleta de colores *Kaizuna*: Azul `#145890`, Verde `#5A8259`, Oro `#D6A77A`).
    *   **JavaScript (Vanilla JS):** Para la interactividad del lado del cliente. Gestiona el envío de mensajes, manipula el DOM (Document Object Model) para renderizar las burbujas de chat de forma dinámica y realiza peticiones asíncronas (`fetch`) a la API de Python.

*   **Estructura del Frontend (`/frontend/`):**
    *   `index.html`: La vista única de la aplicación. Contiene la semántica y estructura básica de la ventana del chatbot.
    *   `style.css`: Estilos visuales del chat. Define las animaciones, tipografías, colores institucionales y disposición responsive para distintos tamaños de pantalla.
    *   `script.js`: Controlador del lado del cliente. Intercepta los eventos de teclado (como presionar la tecla *Enter*) y del botón de enviar, toma el texto, llama al servidor (`POST /api/chat`) y agrega la respuesta recibida a la interfaz gráfica.
