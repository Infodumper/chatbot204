"""
chat.py — Motor de Procesamiento de Lenguaje Natural (NLP) del Chatbot Bot204.

Pipeline basado en los trabajos prácticos de PLN del usuario:
  1. Limpieza y Tokenización (NLTK + Regex)
  2. Autocorrección (Distancia de Levenshtein — Programación Dinámica)
  3. Categorización de Intenciones (Bag of Words)
  4. Ejecución de consultas con Pandas
"""

import re
import pandas as pd
import nltk

# Asegurar que el tokenizador esté descargado (solo se descarga si no existe)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

# Importar carga centralizada de datos (sin dependencia circular)
from backend.data_loader import get_clientes_df, get_pedidos_df, get_lideres_df


# ==============================================================================
# VOCABULARIO Y CATEGORÍAS (BASADO EN TRABAJO DE PLN)
# ==============================================================================

VOCABULARIO = [
    'cumpleaños', 'cumplen', 'mes', 'enero', 'febrero', 'marzo', 'abril',
    'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre',
    'diciembre', 'lider', 'clientes', 'pedidos', 'localidad', 'cuantos',
    'tiene', 'quien', 'quienes', 'cuales', 'compras', 'facturacion',
    'unidades', 'pvp', 'promedio', 'total',
]

CATEGORIAS = {
    'cumpleanos_mes': [
        'cumpleaños', 'cumplen', 'cumple', 'nacimiento', 'mes',
        'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
    ],
    'buscar_lider': ['lider', 'líder', 'equipo', 'tiene'],
    'buscar_localidad': ['localidad', 'ciudad', 'viven', 'pueblo'],
    'buscar_pedidos_cliente': [
        'pedidos', 'compras', 'facturacion', 'unidades', 'pvp', 'promedio',
    ],
}

MESES_NUM = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}

# Palabras que indican que el usuario quiere una lista de nombres.
_PALABRAS_LISTADO = {'quien', 'quienes', 'cuales', 'quién', 'quiénes'}


# ==============================================================================
# MOTOR NLP
# ==============================================================================

class MotorNLP:
    """Motor de Procesamiento de Lenguaje Natural clásico."""

    @staticmethod
    def limpiar_texto(texto: str) -> list:
        """Limpia y tokeniza un texto en una lista de palabras."""
        texto = str(texto).lower()
        texto = re.sub(r'[^a-záéíóúñü0-9\s]', ' ', texto)
        try:
            return nltk.word_tokenize(texto)
        except Exception:
            return texto.split()

    @staticmethod
    def levenshtein_dp(s1: str, s2: str) -> int:
        """Calcula la Distancia de Levenshtein entre dos cadenas (DP)."""
        if not s1: return len(s2)
        if not s2: return len(s1)
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m + 1): dp[i][0] = i
        for j in range(n + 1): dp[0][j] = j
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i - 1] == s2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1
        return dp[m][n]

    @staticmethod
    def autocorregir_palabras(palabras: list) -> list:
        """Autocorrige palabras comparándolas con el VOCABULARIO usando Levenshtein."""
        corregidas = []
        for palabra in palabras:
            if palabra.isnumeric() or len(palabra) <= 3:
                corregidas.append(palabra)
                continue

            mejor_dist = 999
            mejor_candidato = palabra
            for candidata in VOCABULARIO:
                dist = MotorNLP.levenshtein_dp(palabra, candidata)
                if dist < mejor_dist and dist <= 2:
                    mejor_dist = dist
                    mejor_candidato = candidata

            corregidas.append(mejor_candidato)
        return corregidas

    @staticmethod
    def categorizar_intencion(palabras: list) -> str:
        """Clasifica la intención del usuario mediante Bag of Words."""
        mejor_cat = None
        mejor_score = 0
        for cat, keywords in CATEGORIAS.items():
            score = sum(1 for p in palabras if p in keywords)
            if score > mejor_score:
                mejor_score = score
                mejor_cat = cat
        return mejor_cat if mejor_score > 0 else "desconocido"

    @staticmethod
    def buscar_entidad(palabras: list, registros: list, col_nombre: str,
                       col_id: str, excluir: list = None,
                       max_dist: int = 2, buscar_partes: bool = False):
        """
        Búsqueda genérica de una entidad por nombre usando Levenshtein.

        Args:
            palabras:      Lista de palabras del usuario (ya corregidas).
            registros:     Lista de dicts con las entidades candidatas.
            col_nombre:    Clave del dict que contiene el nombre a comparar.
            col_id:        Clave del dict que contiene el ID numérico.
            excluir:       Palabras a ignorar (ej: keywords de la categoría).
            max_dist:      Distancia máxima de Levenshtein aceptada.
            buscar_partes: Si True, compara contra cada parte del nombre
                           (útil para nombres compuestos como "GARCIA LOPEZ MARIA").

        Returns:
            tuple: (id_encontrado, nombre_real) o (None, None).
        """
        excluir = set(excluir or [])
        mejor_dist = 999
        mejor_match = None

        for palabra in palabras:
            if palabra in excluir or len(palabra) <= 3:
                continue
            for item in registros:
                nombre_completo = str(item[col_nombre]).lower()
                partes = nombre_completo.split() if buscar_partes else [nombre_completo]
                for parte in partes:
                    if len(parte) <= 3:
                        continue
                    dist = MotorNLP.levenshtein_dp(palabra, parte)
                    if dist < mejor_dist and dist <= max_dist:
                        mejor_dist = dist
                        mejor_match = item

        if mejor_match:
            return mejor_match[col_id], str(mejor_match[col_nombre]).title()
        return None, None


# ==============================================================================
# HELPERS DE RESPUESTA
# ==============================================================================

def _pide_listado(palabras: list) -> bool:
    """Retorna True si el usuario pide nombres (quién/quiénes/cuáles)."""
    return bool(set(palabras) & _PALABRAS_LISTADO)


def _formatear_lista_nombres(nombres: list, intro: str, limite: int = 10) -> str:
    """Formatea una lista de nombres con truncamiento opcional."""
    total = len(nombres)
    if total == 0:
        return f"{intro}, pero actualmente no tiene registros."
    if total <= limite:
        return f"{intro}. Ellos son: {', '.join(nombres)}."
    return f"{intro}. Algunos de ellos son: {', '.join(nombres[:limite])}..."


# ==============================================================================
# PROCESADOR PRINCIPAL
# ==============================================================================

def procesar_mensaje(mensaje: str) -> str:
    """
    Procesa un mensaje del usuario y devuelve la respuesta del chatbot.

    Pipeline: Limpiar → Autocorregir → Categorizar → Consultar Pandas → Responder.
    """
    # 1. Pipeline NLP
    palabras = MotorNLP.limpiar_texto(mensaje)
    palabras_corregidas = MotorNLP.autocorregir_palabras(palabras)
    intencion = MotorNLP.categorizar_intencion(palabras_corregidas)

    print(f"DEBUG — Original: {mensaje}")
    print(f"DEBUG — Corregidas: {palabras_corregidas}")
    print(f"DEBUG — Intención: {intencion}")

    # 2. Ejecutar la intención detectada
    if intencion == "cumpleanos_mes":
        return _resolver_cumpleanos(palabras_corregidas)

    elif intencion == "buscar_lider":
        return _resolver_lider(palabras_corregidas)

    elif intencion == "buscar_pedidos_cliente":
        return _resolver_pedidos_cliente(palabras_corregidas)

    return (
        "Lo siento, mi motor de NLP aún está aprendiendo. "
        "Prueba preguntando por cumpleaños, líderes o pedidos de un cliente."
    )


# ==============================================================================
# RESOLUCIÓN DE INTENCIONES
# ==============================================================================

def _resolver_cumpleanos(palabras: list) -> str:
    """Resuelve la intención de búsqueda de cumpleaños por mes."""
    mes_detectado = next((m for m in MESES_NUM if m in palabras), None)
    if not mes_detectado:
        return "Entendí que preguntas por cumpleaños, pero no detecté un mes válido."

    df = get_clientes_df()
    df_fechas = pd.to_datetime(df['FecNac'], errors='coerce')
    df_filtrado = df[df_fechas.dt.month == MESES_NUM[mes_detectado]]
    cantidad = df_filtrado.shape[0]
    mes_cap = mes_detectado.capitalize()

    if _pide_listado(palabras):
        if cantidad == 0:
            return f"Nadie cumple años en el mes de {mes_cap}."
        nombres = df_filtrado['Nombre'].tolist()
        return _formatear_lista_nombres(
            nombres, f"Los {cantidad} clientes que cumplen en {mes_cap} son"
        )

    return f"Hay {cantidad} clientes que cumplen años en el mes de {mes_cap}."


def _resolver_lider(palabras: list) -> str:
    """Resuelve la intención de búsqueda por líder (por ID o por nombre)."""
    # Intentar ID numérico directo
    nro_lider = next((int(p) for p in palabras if p.isnumeric()), None)
    nombre_lider = None

    # Si no hay ID, buscar por nombre en lideres.csv
    if not nro_lider:
        df_lideres = get_lideres_df()
        registros = df_lideres[['NombreLider', 'Lider']].dropna().to_dict('records')
        nro_lider, nombre_lider = MotorNLP.buscar_entidad(
            palabras, registros,
            col_nombre='NombreLider', col_id='Lider',
            excluir=CATEGORIAS['buscar_lider'],
        )

    if not nro_lider:
        return "Entendí que buscas por líder. Por favor, indícame el nombre o el número de líder."

    df = get_clientes_df()
    df_filtrado = df[df['Lider'] == nro_lider]
    cantidad = df_filtrado.shape[0]
    etiqueta = f"{nombre_lider} ({nro_lider})" if nombre_lider else str(nro_lider)

    if _pide_listado(palabras):
        if cantidad == 0:
            return f"El líder {etiqueta} actualmente no tiene clientes."
        nombres = df_filtrado['Nombre'].tolist()
        return _formatear_lista_nombres(
            nombres, f"El líder {etiqueta} tiene {cantidad} clientes"
        )

    return f"El líder {etiqueta} tiene actualmente {cantidad} clientes asignados."


def _resolver_pedidos_cliente(palabras: list) -> str:
    """Resuelve la intención de resumen de pedidos por cliente."""
    nro_cliente = next((int(p) for p in palabras if p.isnumeric()), None)
    nombre_cliente = None
    df_clientes = get_clientes_df()

    # Si no hay ID, buscar por nombre
    if not nro_cliente:
        registros = df_clientes[['Nombre', 'Nro']].dropna().to_dict('records')
        nro_cliente, nombre_cliente = MotorNLP.buscar_entidad(
            palabras, registros,
            col_nombre='Nombre', col_id='Nro',
            excluir=CATEGORIAS['buscar_pedidos_cliente'],
            max_dist=1, buscar_partes=True,
        )

    if not nro_cliente:
        return "Entendí que buscas los pedidos de un cliente. Por favor, indícame el nombre o número del cliente."

    # Obtener nombre real si aún no lo tenemos
    if not nombre_cliente:
        match = df_clientes[df_clientes['Nro'] == nro_cliente]
        nombre_cliente = str(match.iloc[0]['Nombre']).title() if not match.empty else str(nro_cliente)

    df_pedidos = get_pedidos_df()
    df_filtrado = df_pedidos[df_pedidos['Nro'] == nro_cliente]
    cantidad = df_filtrado.shape[0]

    if cantidad == 0:
        return f"El cliente {nombre_cliente} ({nro_cliente}) no tiene pedidos registrados."

    unidades_total = df_filtrado['Unidades'].sum()
    unidades_promedio = df_filtrado['Unidades'].mean()
    pvp_total = df_filtrado['PVP'].sum()
    pvp_promedio = df_filtrado['PVP'].mean()

    return (
        f"<strong>Pedidos del cliente {nombre_cliente}:</strong><br>"
        f"• <strong>Cantidad de Pedidos:</strong> {cantidad}<br>"
        f"• <strong>Unidades:</strong> {unidades_total} totales "
        f"({unidades_promedio:.2f} promedio por pedido)<br>"
        f"• <strong>PVP:</strong> ${pvp_total:,.2f} totales "
        f"(${pvp_promedio:,.2f} promedio por pedido)"
    )
