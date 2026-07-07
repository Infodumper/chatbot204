# Manual de Usuario — Bot204

Este manual documenta todas las lógicas internas de procesamiento de datos y lenguaje natural implementadas en el sistema.

---

## 1. Arquitectura de Módulos

El backend se compone de 4 módulos Python con responsabilidades separadas:

| Módulo | Responsabilidad |
|---|---|
| `data_processor.py` | Limpieza de CSVs crudos → CSVs limpios |
| `data_loader.py` | Carga centralizada de DataFrames (punto único de acceso a los datos) |
| `main.py` | API REST (endpoints FastAPI + Swagger) |
| `chat.py` | Motor NLP + resolución de intenciones con Pandas |

---

## 2. Pipeline de Lenguaje Natural (NLP)

El bot cuenta con un motor NLP propio, sin dependencias de modelos externos. Cada mensaje pasa por tres etapas:

### 2.1 Limpieza y Tokenización
- Convierte el texto a minúsculas.
- Elimina signos de puntuación con expresiones regulares.
- Separa la oración en palabras individuales usando `nltk.word_tokenize`.

### 2.2 Autocorrección (Distancia de Levenshtein)
Si el usuario comete un error de tipeo (ej. *"cunpleaños"* o *"maio"*), el sistema calcula la distancia matemática (Levenshtein, Programación Dinámica) entre cada palabra y un vocabulario interno. Si la distancia es ≤ 2, la palabra se autocorrige por su equivalente válido.

### 2.3 Categorización de Intenciones (Bag of Words)
El sistema mantiene un diccionario de categorías con palabras clave asociadas. Asigna puntajes a cada categoría contando las coincidencias exactas y elige la categoría ganadora.

**Intenciones soportadas:**

| Intención | Palabras Clave | Ejemplo de Pregunta |
|---|---|---|
| `cumpleanos_mes` | cumpleaños, cumplen, enero-diciembre... | "¿Cuántos cumplen en mayo?" |
| `buscar_lider` | líder, equipo, tiene | "¿Quiénes son los clientes de Carolina?" |
| `buscar_pedidos_cliente` | pedidos, compras, unidades, pvp | "Pedidos del cliente 141639" |
| `buscar_localidad` | localidad, ciudad, viven | *(en desarrollo)* |

---

## 3. Formatos de Respuesta Dinámicos

- **"¿Cuántos...?"** → Devuelve un número exacto.
- **"¿Quién/Quiénes/Cuáles...?"** → Devuelve una lista de nombres (máximo 10 para no saturar la pantalla).
- **Pedidos de un cliente** → Devuelve un resumen con:
  - Cantidad de pedidos.
  - Unidades totales y promedio por pedido.
  - PVP total y promedio por pedido.

---

## 4. Lógica del Sistema de Líderes

### 4.1 Asignación Dinámica (Última Campaña — CooAA)
Los pedidos se identifican por campañas con formato **CooAA**:
- `C` = Fijo.
- `oo` = Orden cronológico (01, 02... 13).
- `AA` = Año (25, 26...).

Durante el procesamiento de datos (`data_processor.py`), el sistema:
1. Extrae `AA` (año) y `oo` (orden) numéricamente.
2. Ordena los pedidos de cada cliente de mayor a menor (año desc, orden desc).
3. Toma el líder del primer registro (el más reciente).
4. Sobreescribe la columna `Lider` en `clientes_limpio.csv`.

**Resultado:** El líder de un cliente siempre refleja su actividad más reciente.

### 4.2 Búsqueda Fuzzy de Líderes por Nombre
Cuando el usuario pregunta por un líder usando su nombre (ej. *"Carolina"*), el bot:
1. Carga `lideres.csv`.
2. Compara el texto del usuario contra cada `NombreLider` usando Levenshtein.
3. Si encuentra una coincidencia (distancia ≤ 2), obtiene el ID numérico.
4. Filtra `clientes_limpio.csv` con ese ID.

### 4.3 Búsqueda Fuzzy de Clientes por Nombre
Para la intención de pedidos, el bot también puede buscar clientes por nombre. Como los nombres pueden ser compuestos (ej. *"GARCIA LOPEZ MARIA"*), la búsqueda se realiza parte por parte con una tolerancia más estricta (distancia ≤ 1).

---

## 5. Procesamiento de Datos (`data_processor.py`)

### Orden de Ejecución
1. **`clean_pedidos()`** → Genera `pedidos_limpio.csv` y retorna el mapeo de último líder.
2. **`clean_clientes(nro_to_lider)`** → Genera `clientes_limpio.csv` y `lideres.csv`.

### Transformaciones Aplicadas

| Operación | Clientes | Pedidos |
|---|---|---|
| Corrección de encoding (Latin1→UTF8) | ✓ | ✓ |
| Rellenar nulos | ✓ | ✓ |
| Trim de espacios | ✓ | ✓ |
| Normalización a mayúsculas | ✓ | ✓ |
| Eliminación de duplicados | ✓ | ✓ |
| Unificación de columnas (Nombre, Tel, FecNac) | ✓ | — |
| Eliminación de columnas innecesarias | IdCliente, IdClip | IdEnvio, Costo_Rev, Rango, Nombre_Lider |
| Renombrar Cliente → Nombre | ✓ | — |
| Asignación dinámica de Líder (CooAA) | ✓ | — |

---

## 6. Comandos de Prueba

| Pregunta | Respuesta esperada |
|---|---|
| ¿Cuántos clientes cumplen en agosto? | Número de clientes |
| ¿Quiénes cumplen años en marzo? | Lista de nombres |
| ¿Cuántos clientes tiene el líder 140255? | Número de clientes |
| ¿Quiénes son del equipo de Carolina? | Lista de nombres del equipo |
| Pedidos del cliente 141639 | Resumen con unidades y PVP |
| ¿Cuantos cunplen en maio? | Autocorrige y responde correctamente |
