import os
from google import genai
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar API Key
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

def generar_respuesta_amigable(mensaje_usuario: str, dato_duro_pandas: str) -> str:
    """
    Toma el resultado procesado por Pandas (dato_duro_pandas) y el mensaje original,
    y utiliza Gemini para redactar una respuesta amigable.
    """
    if not api_key or api_key == "tu_api_key_aqui":
        return f"*(Modo sin Gemini - Configura GEMINI_API_KEY en .env)*\n\n{dato_duro_pandas}"
    
    prompt = f"""
Eres el Director de Ventas de la empresa, llamado Bot204.
Tu tono debe ser directo y educado.

Tu objetivo es responder a la consulta del usuario basándote ÚNICAMENTE en la información calculada por el sistema.
ESTRICTAMENTE solo puedes responder a preguntas relacionadas con las ventas y los clientes que tenemos cargados.
Si la pregunta del usuario no está relacionada con ventas o clientes, o si la "Información calculada por el sistema" no aporta datos relevantes al respecto, debes negarte cortésmente a responder, indicando que tu enfoque es exclusivo a las ventas y clientes de la compañía.

NO DEBES INVENTAR NÚMEROS, FECHAS NI REALIZAR CÁLCULOS MATEMÁTICOS. El "filtro" son las posibles respuestas del sistema experto.

Mensaje original del usuario: "{mensaje_usuario}"

Información calculada por el sistema (transmite este mismo dato de forma clara, directa y educada, sin alterar los números. Si el texto tiene formato HTML, ignora las etiquetas y extrae el contenido):
"{dato_duro_pandas}"
"""
    
    try:
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
        if client:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            return response.text.strip()
        return dato_duro_pandas
    except Exception as e:
        print(f"Error con Gemini API: {str(e)}")
        return dato_duro_pandas
