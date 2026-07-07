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

## Interfaz de Usuario
- Utilizar paleta de colores Kaizuna (Azul `#145890`, Verde `#5A8259`, Oro `#D6A77A`).
