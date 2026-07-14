"""
data_processor.py — Limpieza y transformación de datos crudos.

Lee los archivos CSV originales de /datos_originales, aplica transformaciones
de limpieza con Pandas (encoding, nulos, duplicados, normalización) y exporta
los resultados a /datos_limpios.

Orden de ejecución:
  1. clean_pedidos()  → pedidos_limpio.csv  (retorna mapeo Nro→Líder más reciente)
  2. clean_clientes() → clientes_limpio.csv + lideres.csv
"""

import pandas as pd
import os

# ==============================================================================
# UTILIDADES COMPARTIDAS
# ==============================================================================

# Mapa de secuencias Latin1 mal decodificadas → caracteres UTF-8 correctos.
_ENCODING_REPLACEMENTS = {
    'Ã\x91': 'Ñ', 'Ã±': 'ñ',
    'Ã¡': 'á', 'Ã©': 'é', 'Ã\xad': 'í', 'Ã³': 'ó', 'Ãº': 'ú',
    'Ã': 'í',
}


def fix_encoding(text):
    """Corrige problemas de codificación Latin1/UTF-8 en cadenas de texto."""
    if pd.isna(text) or not isinstance(text, str):
        return text
    try:
        return text.encode('latin1').decode('utf-8')
    except (UnicodeDecodeError, UnicodeEncodeError):
        for bad, good in _ENCODING_REPLACEMENTS.items():
            text = text.replace(bad, good)
        return text


def _trim_text_columns(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """Elimina espacios sobrantes al inicio y final de columnas de texto."""
    for col in columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: str(x).strip() if pd.notna(x) else x)
    return df


# ==============================================================================
# LIMPIEZA DE PEDIDOS
# ==============================================================================

def clean_pedidos(input_filename="pedidos.csv", output_filename="pedidos_limpio.csv") -> dict:
    """
    Limpia pedidos.csv y calcula el último líder de cada cliente.

    Retorna:
        tuple: (dict de {Nro_cliente: Nro_lider_más_reciente}, DataFrame con estadísticas)
    """
    input_path = os.path.join("datos_originales", input_filename)
    output_dir = "datos_limpios"
    output_path = os.path.join(output_dir, output_filename)

    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(input_path)

    # 1. Rellenar nulos
    df = df.replace('NULL', pd.NA)
    df['Localidad'] = df['Localidad'].fillna('Desconocido')
    df['Provincia'] = df['Provincia'].fillna('Desconocido')
    df['Precio_Envio'] = df['Precio_Envio'].fillna(0.0)

    # 2. Eliminar columnas innecesarias
    df = df.drop(columns=['IdEnvio', 'Costo_Rev', 'Rango'], errors='ignore')

    # 3. Corregir encoding
    df['Nombre'] = df['Nombre'].apply(fix_encoding)
    df['Nombre_Lider'] = df['Nombre_Lider'].apply(fix_encoding)

    # 4. Trim y normalización a mayúsculas
    df = _trim_text_columns(df, ['Nombre', 'Nombre_Lider', 'Localidad', 'Provincia'])
    df['Nombre'] = df['Nombre'].str.upper()
    df['Nombre_Lider'] = df['Nombre_Lider'].str.upper()

    # 5. Eliminar duplicados (mismo pedido = misma Campaña + Nro + Lider)
    df = df.drop_duplicates(subset=['Campaña', 'Nro', 'Lider'], keep='last')

    # 6. Eliminar columna redundante (el nombre del líder ya está en lideres.csv)
    df = df.drop(columns=['Nombre_Lider'], errors='ignore')

    # 7. Guardar CSV limpio
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"[OK] Pedidos limpios guardados en: {output_path}")

    # 8. Calcular el último líder de cada cliente según la campaña (CooAA)
    #    Formato: C + oo (orden) + AA (año). Ej: C0126 → orden=01, año=26
    df_temp = df.dropna(subset=['Campaña', 'Nro', 'Lider']).copy()
    df_temp['AA'] = pd.to_numeric(df_temp['Campaña'].str[-2:], errors='coerce')
    df_temp['oo'] = pd.to_numeric(df_temp['Campaña'].str[1:-2], errors='coerce')
    df_temp = df_temp.sort_values(
        by=['Nro', 'AA', 'oo'], ascending=[True, False, False]
    )
    df_latest = df_temp.drop_duplicates(subset=['Nro'], keep='first')

    nro_to_lider = df_latest.set_index('Nro')['Lider'].to_dict()

    # 9. Agrupamientos (groupby) y Creación de columnas calculadas
    # Calculamos el total de pedidos y facturación histórica por cliente.
    df_stats = df.groupby('Nro').agg(
        Total_Pedidos=('Campaña', 'count'),
        Total_Facturado=('PVP', 'sum')
    ).reset_index()

    return nro_to_lider, df_stats


# ==============================================================================
# LIMPIEZA DE CLIENTES
# ==============================================================================

def clean_clientes(nro_to_lider: dict = None, df_stats: pd.DataFrame = None, input_filename="clientes.csv", output_filename="clientes_limpio.csv"):
    """
    Limpia clientes.csv y genera lideres.csv como tabla derivada.

    Args:
        nro_to_lider: Diccionario {Nro → Lider} proveniente de clean_pedidos().
        df_stats: DataFrame con estadísticas agrupadas de los pedidos (merge).
    """
    input_path = os.path.join("datos_originales", input_filename)
    output_dir = "datos_limpios"
    output_path = os.path.join(output_dir, output_filename)

    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(input_path)

    # 1. Renombrar 'Cliente' → 'Nombre' (unificación con pedidos_limpio)
    if 'Cliente' in df.columns:
        df = df.rename(columns={'Cliente': 'Nombre'})

    # 2. Rellenar valores nulos
    df = df.replace('NULL', pd.NA)
    df['Localidad'] = df['Localidad'].fillna('Desconocido')

    # 3. Corregir encoding
    df['Nombre'] = df['Nombre'].apply(fix_encoding)

    # 4. Unificar nombres (Nombre + Nombre_Clip)
    if 'Nombre_Clip' in df.columns:
        df['Nombre_Clip'] = df['Nombre_Clip'].apply(fix_encoding)
        df['Nombre'] = df['Nombre'].combine_first(df['Nombre_Clip'])
        df = df.drop(columns=['Nombre_Clip'])

    # 5. Trim y normalización
    df = _trim_text_columns(df, ['Nombre', 'Localidad', 'Direccion', 'Email'])
    df['Nombre'] = df['Nombre'].str.upper()

    # 6. Eliminar duplicados
    df = df.drop_duplicates(subset=['Nro', 'Nombre', 'Lider'], keep='last')

    # 7. Formatear Email
    if 'Email' in df.columns:
        df['Email'] = df['Email'].str.lower()

    # 8. Unificar Teléfonos
    if 'Telefono' in df.columns:
        df['Telefono'] = df['Telefono'].astype(str).str.replace(r'\.0$', '', regex=True)
    df['Telefono'] = df['Telefono_Perla'].combine_first(df['Telefono_Clip'])
    df = df.drop(columns=['Telefono_Perla', 'Telefono_Clip'])

    # 9. Unificar Fechas de Nacimiento y Cambio de formato de fechas
    if 'FecNac_Perla' in df.columns and 'FecNac_Clip' in df.columns:
        df['FecNac'] = df['FecNac_Perla'].combine_first(df['FecNac_Clip'])
        df = df.drop(columns=['FecNac_Perla', 'FecNac_Clip'])
        
    if 'FecNac' in df.columns:
        # Convertimos al formato YYYY-MM-DD
        df['FecNac'] = pd.to_datetime(df['FecNac'], errors='coerce', dayfirst=True).dt.strftime('%Y-%m-%d')

    # 10. Unificar IDs
    df = df.drop(columns=['IdCliente', 'IdClip'], errors='ignore')
    df = df.reset_index(drop=True)
    df.insert(0, 'Id', range(1, len(df) + 1))

    # 11. Actualizar el Líder con la última campaña (CooAA)
    if nro_to_lider:
        df['Lider'] = df['Nro'].map(nro_to_lider).combine_first(df['Lider'])

    # 12. Unión (merge) de dos DataFrames (Simulación de merge de 2 CSVs)
    if df_stats is not None:
        df = df.merge(df_stats, on='Nro', how='left')
        df['Total_Pedidos'] = df['Total_Pedidos'].fillna(0).astype(int)
        df['Total_Facturado'] = df['Total_Facturado'].fillna(0.0)

    # 13. Generar tabla de Líderes
    lideres_unicos = df['Lider'].dropna().astype(int).unique()
    lideres_df = pd.DataFrame({'Lider': lideres_unicos})
    nro_to_nombre = df.set_index('Nro')['Nombre'].to_dict()
    lideres_df['NombreLider'] = lideres_df['Lider'].map(nro_to_nombre).str.split().str[0]
    lideres_df = lideres_df.reset_index(drop=True)
    lideres_df.insert(0, 'IdLider', range(1, len(lideres_df) + 1))

    lideres_path = os.path.join(output_dir, "lideres.csv")
    lideres_df.to_csv(lideres_path, index=False, encoding='utf-8')
    print(f"[OK] Líderes guardados en: {lideres_path}")

    # 14. Formatear Lider y NroDoc como texto sin decimales
    for col in ['Lider', 'NroDoc']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True)
            df[col] = df[col].replace({'nan': '', '<NA>': ''})

    # 15. Guardar clientes limpios
    df = df.drop(columns=['NombreLider'], errors='ignore')
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"[OK] Clientes limpios guardados en: {output_path}")


# ==============================================================================
# EJECUCIÓN DIRECTA
# ==============================================================================

if __name__ == "__main__":
    nro_lider_dict, df_estatisticas = clean_pedidos()
    clean_clientes(nro_lider_dict, df_estatisticas)
