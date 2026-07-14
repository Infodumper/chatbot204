# Reglas del Agente (AGENTS.md)

Este archivo contiene las directrices principales y restricciones para el desarrollo del proyecto **Chatbot de Sistema de Ventas**.

## Arquitectura
- **Backend:** Python + FastAPI + Pandas.
- **Frontend:** HTML, CSS, JavaScript (Estilos basados en colores Kaizuna).

## Restricciones y Reglas de Datos
1. **Orígenes de Datos:** Los datos crudos (archivos `.csv`) se encuentran y deben permanecer intactos en el directorio `/datos_originales`.
2. **Datos Limpios:** Todos los datos transformados por Pandas deben exportarse a la carpeta `/datos_limpios` en formato CSV.
3. **Restricción de Base de Datos:** Queda **ESTRICTAMENTE PROHIBIDO** el uso de SQLite o cualquier otro motor de base de datos relacional/NoSQL para el procesamiento. Toda la lectura se realizará directamente desde los archivos CSV limpios a través de Pandas.
4. **Calculos Matemáticos:** Si se integra un modelo de lenguaje (LLM), este *solo* debe utilizarse para redactar respuestas. Bajo ninguna circunstancia el LLM debe realizar cálculos, agrupamientos o filtrados; esa es responsabilidad exclusiva de Pandas.

## Configuración y Reglas del LLM (Gemini)
1. **Librería y Modelo:** Utilizar exclusivamente la librería `google-genai` (no la obsoleta `google.generativeai`). El modelo por defecto debe ser `gemini-3.5-flash`.
2. **Limitación de Alcance (Filtro):** El bot ÚNICAMENTE debe responder a preguntas relacionadas con las ventas y los clientes que tenemos cargados. Si la consulta se desvía o el sistema experto (NLP/Pandas) no encuentra datos relevantes, el LLM debe negarse cortésmente a responder.
3. **Persona y Tono:** El LLM debe asumir el rol de **Asistente de información comercial** de la empresa. El tono tiene que ser directo, educado y profesional.

## Interfaz de Usuario
- Utilizar paleta de colores Kaizuna (Azul `#145890`, Verde `#5A8259`, Oro `#D6A77A`).
