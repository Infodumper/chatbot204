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
    'diciembre', 'lider', 'lideres', 'líder', 'líderes', 'clientes', 'pedidos', 'localidad', 'cuantos',
    'tiene', 'quien', 'quienes', 'cuales', 'compras', 'facturacion',
    'unidades', 'pvp', 'promedio', 'media', 'total', 'mas', 'mayor', 'top', 
    'mejor', 'mejores', 'ventas', 'dinero', 'plata', 'vendio', 'campaña', 'campañas',
    'nombres', 'lista', 'todos', 'dime', 'decime'
]

CATEGORIAS = {
    'buscar_pedidos': [
        'pedidos', 'compras', 'facturacion', 'unidades', 'pvp', 'promedio', 'media', 'campaña', 'campañas',
        'ventas', 'dinero', 'plata', 'vendio', 'mayor', 'mas', 'mejor', 'mejores', 'top'
    ],
    'cumpleanos_mes': [
        'cumpleaños', 'cumplen', 'cumple', 'nacimiento', 'mes',
        'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
    ],
    'buscar_lider': ['lider', 'lideres', 'líder', 'líderes', 'equipo'],
    'buscar_localidad': ['localidad', 'ciudad', 'viven', 'pueblo'],
}

MESES_NUM = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}

# Palabras que indican que el usuario quiere una lista de nombres.
_PALABRAS_LISTADO = {'quien', 'quienes', 'cuales', 'quién', 'quiénes', 'nombres', 'lista', 'dime', 'decime', 'todos', 'que', 'qué', 'hay'}

# Palabras que indican que el usuario quiere una cantidad numerica.
_PALABRAS_CANTIDAD = {'cuantos', 'cuantas', 'cuántos', 'cuántas', 'cantidad', 'total', 'cuanto', 'cuanta'}


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
    def categorizar_intencion(palabras: list) -> tuple:
        """Clasifica la intención del usuario mediante Bag of Words y retorna (intencion, score)."""
        mejor_cat = None
        mejor_score = 0
        for cat, keywords in CATEGORIAS.items():
            score = sum(1 for p in palabras if p in keywords)
            if score > mejor_score:
                mejor_score = score
                mejor_cat = cat
        return (mejor_cat if mejor_score > 0 else "desconocido"), mejor_score

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

def _pide_cantidad(palabras: list) -> bool:
    """Retorna True si el usuario pide una cantidad numérica (cuántos/cuántas)."""
    return bool(set(palabras) & _PALABRAS_CANTIDAD)


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

# Contexto global por usuario para resolver preguntas de seguimiento
USER_CONTEXT = {}

def procesar_mensaje(mensaje: str, username: str = "default") -> str:
    """
    Procesa un mensaje del usuario y devuelve la respuesta del chatbot.

    Pipeline: Limpiar → Autocorregir → Categorizar → Consultar Pandas → Responder.
    Incluye manejo de contexto para consultas como "¿Y en Abril?".
    """
    # 1. Pipeline NLP
    palabras = MotorNLP.limpiar_texto(mensaje)
    palabras_corregidas = MotorNLP.autocorregir_palabras(palabras)
    intencion, score = MotorNLP.categorizar_intencion(palabras_corregidas)

    # 2. Manejo de contexto (seguimiento)
    context = USER_CONTEXT.get(username, {})
    es_seguimiento = "y" in palabras_corregidas or len(palabras_corregidas) <= 3
    
    # Si es una pregunta corta o con conector 'y', y la intención actual es débil (score <= 1)
    if es_seguimiento and score <= 1 and "last_intent" in context:
        intencion = context["last_intent"]
        
    if intencion != "desconocido":
        USER_CONTEXT[username] = {"last_intent": intencion}

    print(f"DEBUG — Original: {mensaje}")
    print(f"DEBUG — Corregidas: {palabras_corregidas}")
    print(f"DEBUG — Intención final: {intencion} (Score original: {score})")

    # 2. Ejecutar la intención detectada
    if intencion == "cumpleanos_mes":
        return _resolver_cumpleanos(palabras_corregidas)

    elif intencion == "buscar_lider":
        return _resolver_lider(palabras_corregidas)

    elif intencion == "buscar_pedidos":
        return _resolver_pedidos(palabras_corregidas)

    return (
        "No cuento con información sobre esa consulta en este momento. "
        "Recuerda que solo respondo a consultas relacionadas con ventas, clientes cargados, líderes y pedidos."
    )


# ==============================================================================
# RESOLUCIÓN DE INTENCIONES
# ==============================================================================

def _resolver_cumpleanos(palabras: list) -> str:
    """Resuelve la intención de búsqueda de cumpleaños por mes o por cliente."""
    mes_detectado = next((m for m in MESES_NUM if m in palabras), None)
    df = get_clientes_df()
    
    if not mes_detectado:
        # Intentar buscar por cliente
        # Excluir palabras de la intención y palabras comunes/verbos que puedan chocar con apellidos
        palabras_a_excluir = set(CATEGORIAS['cumpleanos_mes']) | set(VOCABULARIO) | {
            'dime', 'decime', 'diez', 'cinco', 'los', 'las', 'que', 'tengas', 
            'registrado', 'registrados', 'tienen', 'tiene', 'del', 'para', 'por', 'como'
        }
        registros = df[['Nombre', 'Nro']].dropna().to_dict('records')
        nro_cliente, nombre_cliente = MotorNLP.buscar_entidad(
            palabras, registros,
            col_nombre='Nombre', col_id='Nro',
            excluir=palabras_a_excluir,
            max_dist=1, buscar_partes=True,
        )
        
        if nro_cliente:
            cliente_data = df[df['Nro'] == nro_cliente].iloc[0]
            fec_nac = cliente_data.get('FecNac')
            if pd.isna(fec_nac) or str(fec_nac).strip() == '':
                return f"No tengo registrada la fecha de nacimiento de {nombre_cliente}."
            
            try:
                # pandas to_datetime maneja bien el parseo, pero en caso de fechas raras o incompletas (ej 0000-00-00), fallará y caerá en el except
                fecha = pd.to_datetime(fec_nac, dayfirst=True)
                meses_es = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                nombre_mes = meses_es[fecha.month - 1]
                return f"El cumpleaños de <strong>{nombre_cliente}</strong> es el <strong>{fecha.day} de {nombre_mes}</strong>."
            except Exception:
                return f"El cumpleaños de {nombre_cliente} está registrado como: {fec_nac}."

        return "Entendí que preguntas por cumpleaños, pero no detecté un mes válido ni el nombre de un cliente."

    df_fechas = pd.to_datetime(df['FecNac'], errors='coerce')
    df_filtrado = df[df_fechas.dt.month == MESES_NUM[mes_detectado]]
    cantidad = df_filtrado.shape[0]
    mes_cap = mes_detectado.capitalize()

    if _pide_cantidad(palabras):
        return f"En {mes_cap} cumplen años <strong>{cantidad}</strong> clientes."

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
    # Intentar ID numérico directo, asegurándose que no sea un año (ej. 2025)
    nro_lider = next((int(p) for p in palabras if p.isnumeric() and not (len(p) == 4 and p.startswith('20'))), None)
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
        # Si piden cantidad (ej. "cuantos lideres hay")
        if _pide_cantidad(palabras):
            df_lideres = get_lideres_df()
            return f"Actualmente hay {len(df_lideres)} líderes registrados."
            
        # Si piden una lista o nombres, devolver todos los líderes
        if _pide_listado(palabras) or 'nombres' in palabras or 'todos' in palabras:
            df_lideres = get_lideres_df()
            if df_lideres.empty:
                return "Actualmente no hay líderes registrados."
            nombres = df_lideres['NombreLider'].dropna().tolist()
            return _formatear_lista_nombres(nombres, "Los líderes registrados son", limite=20)
            
        return "Entendí que buscas por líder. Por favor, indícame el nombre o el número de líder."

    df = get_clientes_df()
    df_filtrado = df[df['Lider'] == nro_lider]
    cantidad = df_filtrado.shape[0]
    etiqueta = f"{nombre_lider} ({nro_lider})" if nombre_lider else str(nro_lider)

    if _pide_cantidad(palabras):
        return f"El líder {etiqueta} tiene <strong>{cantidad}</strong> clientes."

    if _pide_listado(palabras):
        if cantidad == 0:
            return f"El líder {etiqueta} actualmente no tiene clientes."
        nombres = df_filtrado['Nombre'].tolist()
        return _formatear_lista_nombres(
            nombres, f"El líder {etiqueta} tiene {cantidad} clientes"
        )

    return f"El líder {etiqueta} tiene actualmente {cantidad} clientes asignados."


def _resolver_pedidos(palabras: list) -> str:
    """Resuelve la intención de resumen de pedidos (Top, Lider, Cliente o Global)."""
    es_lider = bool(set(palabras) & set(CATEGORIAS['buscar_lider']))
    es_campana = bool(set(palabras) & {'campaña', 'campañas'})
    es_top = bool(set(palabras) & {'mas', 'más', 'mayor', 'top', 'mejor', 'mejores'})
    es_promedio = bool(set(palabras) & {'promedio', 'media'})
    es_unidades = 'unidades' in palabras
    es_pvp = bool(set(palabras) & {'facturacion', 'facturación', 'pvp', 'plata', 'dinero', 'ventas', 'vendio', 'vendió'})
    metrica = 'PVP' if es_pvp else ('Unidades' if es_unidades else 'Pedidos')
    
    df_pedidos = get_pedidos_df()
    if df_pedidos.empty:
        return "No hay pedidos registrados."

    # 1. Filtros temporales (Campaña / Mes)
    campanas_unicas = [str(c).lower() for c in df_pedidos['Campaña'].unique()]
    filtro_campana = next((p for p in palabras if p in campanas_unicas), None)
    mes_aplicado = None
    
    if not filtro_campana:
        mes_detectado = next((m for m in MESES_NUM if m in palabras), None)
        anio_detectado = next((p for p in palabras if p.isnumeric() and len(p) == 4 and p.startswith('20')), None)
        if mes_detectado:
            mes_num = MESES_NUM[mes_detectado]
            if anio_detectado:
                filtro_campana = f"c{mes_num:02d}{anio_detectado[-2:]}"
            else:
                mes_aplicado = mes_detectado.capitalize()
                prefix = f"c{mes_num:02d}"
                df_pedidos = df_pedidos[df_pedidos['Campaña'].str.lower().str.startswith(prefix)]
                if df_pedidos.empty:
                    return f"No hay pedidos registrados para el mes de {mes_aplicado}."
    
    if filtro_campana:
        df_pedidos = df_pedidos[df_pedidos['Campaña'].str.lower() == filtro_campana]
        if df_pedidos.empty:
            return f"No hay pedidos registrados para la campaña {filtro_campana.upper()}."

    # 2. Buscar Entidad (Cliente o Líder)
    nombres_a_excluir = set(CATEGORIAS['buscar_pedidos']) | set(CATEGORIAS['buscar_lider']) | {'mas', 'más', 'mayor', 'top', 'mejor', 'mejores', 'que', 'fue', 'hizo', 'la', 'el', 'las', 'los', 'general', 'empresa', 'total', 'todos', 'todas'}
    nombres_a_excluir.update(MESES_NUM.keys())
    nombres_a_excluir.update(p for p in palabras if p.isnumeric() and len(p) == 4 and p.startswith('20'))
    if filtro_campana: nombres_a_excluir.add(filtro_campana)
    
    posibles_nombres = [p for p in palabras if p not in nombres_a_excluir]
    
    filtro_entidad_nro = None
    filtro_entidad_nombre = None
    filtro_tipo = None
    
    # Intentar buscar Lider directo por ID
    if es_lider:
        nro_directo = next((int(p) for p in palabras if p.isnumeric() and p not in nombres_a_excluir), None)
        if nro_directo:
            filtro_entidad_nro = nro_directo
            filtro_tipo = 'Lider'
            match = get_lideres_df()[get_lideres_df()['Lider'] == nro_directo]
            filtro_entidad_nombre = str(match.iloc[0]['NombreLider']).title() if not match.empty else str(nro_directo)

    # Intentar buscar Cliente directo por ID
    if not es_lider and not filtro_entidad_nro:
        nro_directo = next((int(p) for p in palabras if p.isnumeric() and p not in nombres_a_excluir), None)
        if nro_directo:
            filtro_entidad_nro = nro_directo
            filtro_tipo = 'Nro'
            match = get_clientes_df()[get_clientes_df()['Nro'] == nro_directo]
            filtro_entidad_nombre = str(match.iloc[0]['Nombre']).title() if not match.empty else str(nro_directo)

    if posibles_nombres and not filtro_entidad_nro:
        # Buscar en Lideres si es lider explícito o si no se sabe
        df_lideres = get_lideres_df()
        reg_lideres = df_lideres[['NombreLider', 'Lider']].dropna().to_dict('records')
        id_l, nombre_l = MotorNLP.buscar_entidad(
            posibles_nombres, reg_lideres, 'NombreLider', 'Lider', max_dist=1, buscar_partes=True
        )
        if id_l and (es_lider or not es_top):
            filtro_entidad_nro = id_l
            filtro_entidad_nombre = nombre_l
            filtro_tipo = 'Lider'
        elif not es_lider:
            df_clientes = get_clientes_df()
            reg_clientes = df_clientes[['Nombre', 'Nro']].dropna().to_dict('records')
            id_c, nombre_c = MotorNLP.buscar_entidad(
                posibles_nombres, reg_clientes, 'Nombre', 'Nro', max_dist=1, buscar_partes=True
            )
            if id_c:
                filtro_entidad_nro = id_c
                filtro_entidad_nombre = nombre_c
                filtro_tipo = 'Nro'

    # 3. Aplicar Filtro de Entidad si se encontró y no es Top
    # Si es Top, el filtro de entidad restringe la búsqueda a ese grupo (ej: top cliente del lider X)
    if filtro_entidad_nro:
        df_pedidos = df_pedidos[df_pedidos[filtro_tipo] == filtro_entidad_nro]
        if df_pedidos.empty:
            return f"No hay pedidos registrados para {filtro_entidad_nombre}."

    texto_campana = f" en la campaña <strong>{filtro_campana.upper()}</strong>" if filtro_campana else (f" en el mes de <strong>{mes_aplicado}</strong>" if mes_aplicado else "")
    texto_promedio = " promedio" if es_promedio else ""
    filtro_str = f" para <strong>{filtro_entidad_nombre}</strong>" if filtro_entidad_nombre else ""

    # 4. Resolver Top (Agrupación)
    if es_top:
        if es_lider and not filtro_entidad_nro: col_agrupacion = 'Lider'
        elif es_campana and not filtro_campana: col_agrupacion = 'Campaña'
        else: col_agrupacion = 'Nro'
        
        if metrica == 'Pedidos':
            agrupado = df_pedidos.groupby(col_agrupacion).size().reset_index(name='Total')
        else:
            if es_promedio:
                agrupado = df_pedidos.groupby(col_agrupacion)[metrica].mean().reset_index(name='Total')
            else:
                agrupado = df_pedidos.groupby(col_agrupacion)[metrica].sum().reset_index(name='Total')
                
        agrupado = agrupado.sort_values('Total', ascending=False)
        if agrupado.empty: return "No hay datos suficientes para calcular esto."
        
        top_id = agrupado.iloc[0][col_agrupacion]
        top_total = agrupado.iloc[0]['Total']
        
        if col_agrupacion == 'Campaña': sujeto_str = f"La campaña <strong>{top_id}</strong>"
        elif col_agrupacion == 'Lider':
            match = get_lideres_df()[get_lideres_df()['Lider'] == top_id]
            nombre = str(match.iloc[0]['NombreLider']).title() if not match.empty else str(top_id)
            sujeto_str = f"El líder <strong>{nombre}</strong> ({top_id})"
        else:
            match = get_clientes_df()[get_clientes_df()['Nro'] == top_id]
            nombre = str(match.iloc[0]['Nombre']).title() if not match.empty else str(top_id)
            sujeto_str = f"El cliente <strong>{nombre}</strong> ({top_id})"
            
        if metrica == 'Pedidos': return f"{sujeto_str} tiene la mayor cantidad de pedidos{texto_promedio}{filtro_str}{texto_campana}: <strong>{top_total:.1f}</strong>."
        elif metrica == 'Unidades': return f"{sujeto_str} tiene la mayor cantidad de unidades pedidas{texto_promedio}{filtro_str}{texto_campana}: <strong>{top_total:.1f}</strong>."
        else:
            palabra_fac = "facturación promedio" if es_promedio else "facturación"
            return f"{sujeto_str} tiene la mayor {palabra_fac}{filtro_str}{texto_campana}: <strong>${top_total:,.2f}</strong>."

    # 5. Resolver Entidad o Global
    if filtro_entidad_nro and filtro_tipo == 'Lider':
        # Mostrar resumen de Líder
        cantidad_pedidos = df_pedidos.shape[0]
        campanas_unicas = df_pedidos['Campaña'].nunique()
        promedio_pedidos_campana = cantidad_pedidos / campanas_unicas if campanas_unicas > 0 else 0
        unidades_total = df_pedidos['Unidades'].sum()
        unidades_promedio = df_pedidos['Unidades'].mean()
        unidades_promedio_campana = unidades_total / campanas_unicas if campanas_unicas > 0 else 0
        pvp_total = df_pedidos['PVP'].sum()
        pvp_promedio = df_pedidos['PVP'].mean()
        pvp_promedio_campana = pvp_total / campanas_unicas if campanas_unicas > 0 else 0
        
        return (
            f"<strong>Pedidos del líder {filtro_entidad_nombre}{texto_campana}:</strong><br>"
            f"• <strong>Campañas:</strong> {campanas_unicas}<br>"
            f"• <strong>Cantidad de Pedidos:</strong> {cantidad_pedidos} totales ({promedio_pedidos_campana:.2f} promedio por campaña)<br>"
            f"• <strong>Unidades:</strong> {unidades_total} totales ({unidades_promedio:.2f} promedio por pedido, {unidades_promedio_campana:.2f} promedio por campaña)<br>"
            f"• <strong>PVP:</strong> ${pvp_total:,.2f} totales (${pvp_promedio:,.2f} promedio por pedido, ${pvp_promedio_campana:,.2f} promedio por campaña)"
        )
        
    elif filtro_entidad_nro and filtro_tipo == 'Nro':
        # Mostrar resumen de Cliente
        cantidad_pedidos = df_pedidos.shape[0]
        unidades_total = df_pedidos['Unidades'].sum()
        unidades_media = df_pedidos['Unidades'].mean()
        unidades_mediana = df_pedidos['Unidades'].median()
        pvp_total = df_pedidos['PVP'].sum()
        pvp_media = df_pedidos['PVP'].mean()
        pvp_mediana = df_pedidos['PVP'].median()
        
        return (
            f"<strong>Pedidos del cliente {filtro_entidad_nombre}{texto_campana}:</strong><br>"
            f"• <strong>Cantidad de Pedidos:</strong> {cantidad_pedidos}<br>"
            f"• <strong>Unidades:</strong> {unidades_total} totales ({unidades_media:.2f} media, {unidades_mediana:.2f} mediana por pedido)<br>"
            f"• <strong>PVP:</strong> ${pvp_total:,.2f} totales (${pvp_media:,.2f} media, ${pvp_mediana:,.2f} mediana por pedido)"
        )
        
    else:
        # 6. Global Stats (no entity found)
        # Check if they explicitly wanted a specific entity but we couldn't find it
        if posibles_nombres and not (filtro_campana or mes_aplicado or es_promedio or es_unidades or es_pvp):
            return "Entendí que buscas pedidos de alguien, pero no encontré ese nombre. Por favor, sé más específico o usa el número de cliente/líder."
            
        cantidad_pedidos = df_pedidos.shape[0]
        unidades_total = df_pedidos['Unidades'].sum()
        unidades_media = df_pedidos['Unidades'].mean()
        pvp_total = df_pedidos['PVP'].sum()
        pvp_media = df_pedidos['PVP'].mean()
        
        titulo = f"<strong>Resumen global de ventas{texto_campana}:</strong><br>"
        if metrica == 'PVP' and es_promedio:
            return f"{titulo}La facturación promedio por pedido fue de <strong>${pvp_media:,.2f}</strong> (Total: ${pvp_total:,.2f} en {cantidad_pedidos} pedidos)."
        if metrica == 'Unidades' and es_promedio:
            return f"{titulo}Se pidieron en promedio <strong>{unidades_media:.2f}</strong> unidades por pedido (Total: {unidades_total} en {cantidad_pedidos} pedidos)."
            
        return (
            f"{titulo}"
            f"• <strong>Cantidad de Pedidos:</strong> {cantidad_pedidos}<br>"
            f"• <strong>Unidades:</strong> {unidades_total} totales ({unidades_media:.2f} media por pedido)<br>"
            f"• <strong>PVP:</strong> ${pvp_total:,.2f} totales (${pvp_media:,.2f} media por pedido)"
        )
