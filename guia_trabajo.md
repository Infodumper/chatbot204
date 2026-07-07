# Guía de Trabajo Práctico Integrador: Chatbot

A continuación, se detalla la guía estructurada para el desarrollo del trabajo, basada en los requisitos extraídos del documento:

## Tecnologías obligatorias
El proyecto deberá desarrollarse utilizando las siguientes herramientas y lenguajes:
- **Agente de desarrollo:** OpenCode.
- **Backend/Procesamiento:** Python, FastAPI, Pandas.
- **Frontend:** HTML, CSS, JavaScript.

## Arquitectura esperada
El flujo de la aplicación debe seguir la siguiente estructura:
1. **Usuario**
2. **Interfaz Web** (HTML + CSS + JavaScript)
3. **FastAPI** (Recepción de peticiones)
4. **Python + Pandas** (Lógica y manipulación de datos)
5. **Procesamiento de datos**
6. **Respuesta del chatbot**

## Procesamiento de datos
Antes de poder responder a las consultas de los usuarios, la aplicación deberá realizar tareas de preparación y limpieza de los datos. Se requiere incluir, como mínimo, algunas de las siguientes operaciones usando **Pandas**:
- Eliminación de registros duplicados.
- Tratamiento de valores nulos.
- Conversión de tipos de datos.
- Cambio de formato de fechas.
- Unión (merge) de dos archivos CSV.
- Agrupamientos (`groupby`).
- Ordenamiento de información.
- Creación de nuevas columnas calculadas.

## Interfaz gráfica
El chatbot debe contar con una interfaz web sencilla. No se evaluará el diseño gráfico, sino el correcto funcionamiento.
La página debe contener:
- Un título.
- Un área donde se visualice la conversación.
- Un cuadro de texto para escribir las preguntas.
- Un botón para enviar la consulta.

## API
La aplicación deberá exponer una API construida con **FastAPI**.
- Se requiere, como mínimo, un endpoint que reciba la consulta y devuelva la respuesta.
- **Ejemplo:**
  - `POST /chat`
  - **Entrada (JSON):** `{"question": "¿Cuál fue el producto más vendido?"}`
  - **Salida (JSON):** `{"answer": "El producto más vendido fue..."}`

## Uso de Inteligencia Artificial
- **OpenCode** deberá utilizarse durante todo el desarrollo del proyecto.
- Se espera que se construya la aplicación mediante *prompts* claros y específicos (solicitando mejoras, corrigiendo errores y refinando el código).
- Se evaluará la capacidad del grupo para dirigir correctamente al agente de IA.

## Bonus (Opcional)
- Posibilidad de integrar una API externa de Inteligencia Artificial (ej. OpenRouter, Groq o Gemini).
- **Restricción importante:** La IA integrada **no** debe realizar cálculos sobre los datos. Todos los cálculos deben hacerse con Python y Pandas.
- La IA solo podrá utilizarse para transformar los resultados obtenidos en respuestas más naturales y amigables para el usuario.

## El Resto (Temáticas, Entregables y Desafíos)

### Temática elegida
El proyecto se centrará en un **Sistema de ventas**, utilizando `clientes.csv` y `ventas.csv`.

### Desafío adicional
El chatbot deberá ser capaz de responder preguntas que no fueron programadas de manera exacta. Es decir, debe entender distintas formas de redactar una misma consulta (ej. "¿Cuál fue el producto más vendido?", "¿Qué cliente compró más?", "¿Cuál fue la categoría con mayores ventas?") y producir la misma respuesta.

### Entregables
- Código fuente completo.
- Archivos CSV utilizados.
- Archivo `requirements.txt`.
- Archivo `README.md` con instrucciones de instalación y ejecución.
- Capturas de pantalla del funcionamiento del chatbot.

### Criterios de evaluación
- Correcto uso de OpenCode y claridad de los prompts.
- Organización del proyecto y documentación.
- Funcionamiento de la API (FastAPI) y la interfaz web.
- Procesamiento de datos, limpieza y merge mediante Pandas.
- Calidad de las respuestas del chatbot.
