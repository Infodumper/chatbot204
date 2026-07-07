"""
data_loader.py — Carga centralizada de DataFrames limpios.

Provee funciones reutilizables para leer los CSV de /datos_limpios.
Tanto main.py (API REST) como chat.py (NLP) importan de aquí,
eliminando la dependencia circular entre módulos.
"""

import os
import pandas as pd

# Ruta base del proyecto (un nivel arriba de /backend)
_BASE_DIR = os.path.dirname(os.path.dirname(__file__))
_DATOS_LIMPIOS = os.path.join(_BASE_DIR, "datos_limpios")


def get_clientes_df() -> pd.DataFrame:
    """Carga y retorna el DataFrame de clientes limpios."""
    ruta = os.path.join(_DATOS_LIMPIOS, "clientes_limpio.csv")
    return pd.read_csv(ruta).fillna("")


def get_pedidos_df() -> pd.DataFrame:
    """Carga y retorna el DataFrame de pedidos limpios."""
    ruta = os.path.join(_DATOS_LIMPIOS, "pedidos_limpio.csv")
    if os.path.exists(ruta):
        return pd.read_csv(ruta).fillna("")
    return pd.DataFrame()


def get_lideres_df() -> pd.DataFrame:
    """Carga y retorna el DataFrame de líderes."""
    ruta = os.path.join(_DATOS_LIMPIOS, "lideres.csv")
    return pd.read_csv(ruta).fillna("")
