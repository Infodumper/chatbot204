# Arquitectura Técnica del Chatbot Bot204

Este documento detalla la arquitectura interna del chatbot, incluyendo el flujo completo desde que el usuario escribe un mensaje hasta que recibe la respuesta.

## Diagrama de Flujo

```
Usuario (Frontend)
  │
  ▼
POST /api/chat  ──►  main.py (FastAPI)
                         │
                         ▼
                     chat.py
                    ┌────────────────────────────────┐
                    │  1. Limpiar texto (NLTK + re)  │
                    │  2. Autocorregir (Levenshtein) │
                    │  3. Categorizar (Bag of Words) │
                    └────────────┬───────────────────┘
                                 │
                                 ▼
                     data_loader.py  ──►  datos_limpios/*.csv
                                 │
                                 ▼
                    Pandas filtra, agrupa, calcula
                                 │
                                 ▼
                     Respuesta HTML al frontend
```

## Módulos del Backend

### `data_loader.py` (Carga de Datos)
Punto único de acceso a los DataFrames. Funciones:
- `get_clientes_df()` → Lee `clientes_limpio.csv`
- `get_pedidos_df()` → Lee `pedidos_limpio.csv`
- `get_lideres_df()` → Lee `lideres.csv`

Tanto `main.py` como `chat.py` importan de aquí, eliminando la dependencia circular que existía antes.

### `data_processor.py` (Limpieza)
Script ejecutable que transforma los CSVs crudos de `/datos_originales` en CSVs limpios en `/datos_limpios`.

Funciones principales:
- `fix_encoding(text)` — Utilidad compartida para corregir encoding Latin1/UTF-8.
- `clean_pedidos()` — Limpia pedidos y calcula el mapeo de último líder (CooAA).
- `clean_clientes(nro_to_lider)` — Limpia clientes, aplica el líder dinámico, genera `lideres.csv`.

### `chat.py` (Motor NLP)
Contiene la clase `MotorNLP` y las funciones de resolución de intenciones:

| Clase/Función | Propósito |
|---|---|
| `MotorNLP.limpiar_texto()` | Tokenización con NLTK |
| `MotorNLP.levenshtein_dp()` | Distancia de edición (DP) |
| `MotorNLP.autocorregir_palabras()` | Corrección contra VOCABULARIO |
| `MotorNLP.categorizar_intencion()` | Clasificación Bag of Words |
| `MotorNLP.buscar_entidad()` | Búsqueda fuzzy genérica (líderes y clientes) |
| `_resolver_cumpleanos()` | Intención: cumpleaños por mes |
| `_resolver_lider()` | Intención: búsqueda por líder |
| `_resolver_pedidos_cliente()` | Intención: resumen de pedidos |

### `main.py` (API REST)
Servidor FastAPI que expone:
- Endpoints REST para consultas directas (Swagger UI en `/docs`).
- `POST /api/chat` para el chatbot del frontend.
- Servicio de archivos estáticos del frontend.

## Regla Fundamental

> **Pandas hace el trabajo pesado. El NLP solo categoriza la pregunta.**
> 
> Bajo ninguna circunstancia el motor NLP realiza cálculos, agrupamientos o filtrados. Eso es responsabilidad exclusiva de Pandas.
