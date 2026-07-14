# Manual de Usuario — Bot204

Este manual documenta todas las lógicas internas de procesamiento de datos, lenguaje natural y autenticación implementadas en el sistema.

---

## 1. Arquitectura de Módulos

El backend se compone de 5 módulos Python con responsabilidades separadas:

| Módulo | Responsabilidad |
|---|---|
| `auth.py` | Autenticación de usuarios (SHA-256) y gestión de sesiones en memoria |
| `data_processor.py` | Limpieza de CSVs crudos → CSVs limpios |
| `data_loader.py` | Carga centralizada de DataFrames (punto único de acceso a los datos) |
| `main.py` | API REST (endpoints FastAPI), autenticación Bearer y servidor de frontend |
| `chat.py` | Motor NLP + resolución de intenciones con Pandas |
| `gemini_service.py` | Envío del resultado calculado al LLM para su redacción amigable |

---

## 2. Sistema de Autenticación

### 2.1 Usuarios y Contraseñas
El sistema cuenta con un registro de usuarios definido a través de variables de entorno en el archivo `.env` (`ADMIN_USERNAME`, `ADMIN_PASSWORD`, `USER_USERNAME`, `USER_PASSWORD`). 
Por motivos de seguridad, las contraseñas no se exponen en esta documentación. En el módulo `backend/auth.py` estas credenciales se cargan en memoria y las contraseñas se almacenan internamente aplicando hashing con **SHA-256** (nunca en texto plano). Si no se provee el archivo `.env`, el sistema utilizará unas credenciales por defecto para propósitos de desarrollo.

### 2.2 Flujo de Login
1. El usuario ingresa sus credenciales en el modal de login (frontend).
2. El frontend envía un `POST /api/login` con `username` y `password`.
3. El backend hashea la contraseña recibida, la compara contra el hash almacenado.
4. Si coincide, genera un token seguro (`secrets.token_hex(32)`) y lo devuelve.
5. El frontend guarda el token en `localStorage` y lo adjunta como header `Authorization: Bearer <token>` en todas las peticiones posteriores a `/api/chat`.

### 2.3 Protección de Endpoints
- `POST /api/login` → **público** (no requiere token).
- `POST /api/chat` → **protegido** (requiere token Bearer válido).
- Endpoints REST de Swagger (`/clientes`, `/pedidos`, etc.) → actualmente públicos.

### 2.4 Limitaciones
- Las sesiones viven en un diccionario de Python en memoria. **Se pierden al reiniciar el servidor.**
- No hay expiración automática de tokens.
- Si el backend devuelve un error 401, el frontend cierra la sesión automáticamente y redirige al modal de login.

---

## 3. Pipeline de Lenguaje Natural (NLP)

El bot cuenta con un motor NLP propio, sin dependencias de modelos externos. Cada mensaje pasa por tres etapas:

### 3.1 Limpieza y Tokenización
- Convierte el texto a minúsculas.
- Elimina signos de puntuación con expresiones regulares.
- Separa la oración en palabras individuales usando `nltk.word_tokenize`.

### 3.2 Autocorrección (Distancia de Levenshtein)
Si el usuario comete un error de tipeo (ej. *"cunpleaños"* o *"maio"*), el sistema calcula la distancia matemática (Levenshtein, Programación Dinámica) entre cada palabra y un vocabulario interno. Si la distancia es ≤ 2, la palabra se autocorrige por su equivalente válido.

### 3.3 Categorización de Intenciones (Bag of Words)
El sistema mantiene un diccionario de categorías con palabras clave asociadas. Asigna puntajes a cada categoría contando las coincidencias exactas y elige la categoría ganadora.

**Intenciones soportadas:**

| Intención | Palabras Clave | Ejemplo de Pregunta |
|---|---|---|
| `cumpleanos_mes` | cumpleaños, cumplen, enero-diciembre... | "¿Cuántos cumplen en mayo?" |
| `buscar_lider` | líder, equipo, tiene | "¿Quiénes son los clientes de Carolina?" |
| `buscar_pedidos` | pedidos, compras, unidades, pvp, campaña, mas, top | "Pedidos de 141639" / "¿Qué campaña vendió más?" |
| `buscar_localidad` | localidad, ciudad, viven | *(en desarrollo)* |

---

## 4. Formatos de Respuesta Dinámicos

- **"¿Cuántos...?"** → Devuelve un número exacto.
- **"¿Quién/Quiénes/Cuáles...?"** → Devuelve una lista de nombres (máximo 10 para no saturar la pantalla).
- **Pedidos de un cliente** → Devuelve un resumen con:
  - Cantidad de pedidos.
  - Unidades: Totales, media y mediana por pedido.
  - PVP: Total, media y mediana por pedido.
- **Pedidos de un líder** → Devuelve un resumen con:
  - Cantidad de campañas y de pedidos (con promedio de pedidos por campaña).
  - Unidades: Totales, promedio por pedido y promedio por campaña.
  - PVP: Total, promedio por pedido y promedio por campaña.
- **Top / Rankings ("¿Qué líder...", "¿Qué campaña...")** → Resuelve consultas de máximos dinámicos. Extrae automáticamente la entidad mencionada (ej: "Estevez"), filtra los datos, agrupa por Campaña, Líder o Cliente (según lo pedido), y calcula quién obtuvo más:
  - Pedidos ("más pedidos").
  - Unidades ("más unidades").
  - Facturación/PVP ("más PVP", "mayor facturación", "más ventas").

---

## 5. Redacción con Google Gemini (LLM)

Para que las respuestas sean fluidas y amigables, se ha integrado la API de **Google Gemini** (`gemini_service.py`).
El flujo de una respuesta es el siguiente:
1. El motor NLP procesa la consulta (Sección 3).
2. Pandas filtra y calcula el *Dato Duro* (Sección 4).
3. Este "Dato Duro" se inyecta en un *prompt de sistema* que se envía a Gemini.
4. Se le prohíbe explícitamente a Gemini realizar cálculos aritméticos, inventar números o modificar la verdad del dato. Su única función es la **redacción** amigable (agregar emojis, saludar, formatear de manera conversacional).

> **Nota:** Si la API Key de Gemini (`GEMINI_API_KEY` en el archivo `.env`) no está configurada, el sistema automáticamente hace *fallback* y devuelve el dato duro calculado por Pandas.

---

## 6. Lógica del Sistema de Líderes

### 6.1 Asignación Dinámica (Última Campaña — CooAA)
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

### 6.2 Búsqueda Fuzzy de Líderes por Nombre
Cuando el usuario pregunta por un líder usando su nombre (ej. *"Carolina"*), el bot:
1. Carga `lideres.csv`.
2. Compara el texto del usuario contra cada `NombreLider` usando Levenshtein.
3. Si encuentra una coincidencia (distancia ≤ 2), obtiene el ID numérico.
4. Filtra `clientes_limpio.csv` con ese ID.

### 6.3 Búsqueda Fuzzy de Clientes por Nombre
Para la intención de pedidos, el bot también puede buscar clientes por nombre. Como los nombres pueden ser compuestos (ej. *"GARCIA LOPEZ MARIA"*), la búsqueda se realiza parte por parte con una tolerancia más estricta (distancia ≤ 1).

---

## 7. Procesamiento de Datos (`data_processor.py`)

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
| Formatear Lider y NroDoc como texto (sin .0) | ✓ | — |
| Merge con estadísticas de pedidos | ✓ | — |

---

## 8. Interfaz de Usuario (Frontend)

### 8.1 Barra Lateral Izquierda
La barra lateral contiene (de arriba a abajo):
- **Logo** del proyecto.
- **Nombre:** "Bot204".
- **Iconos decorativos** (Phosphor Icons): Equipo, Swagger (abre `/docs` en pestaña nueva), Agentes IA.
- **Botón de tema** claro/oscuro (sol/luna).
- **Nombre del usuario** logueado (al hacer clic, despliega opción "Cerrar sesión").

### 8.2 Área Principal
- Cabecera con título "Comunicación Interna".
- Panel lateral de consultas (lista de conversaciones).
- Ventana de chat con mensajes del usuario y del bot.
- Input de texto con envío por Enter o botón.

### 8.3 Temas
El sistema soporta modo **claro** y **oscuro**. La preferencia se guarda en `localStorage` y persiste entre sesiones.

---

## 9. Comandos de Prueba

| Pregunta | Respuesta esperada |
|---|---|
| ¿Cuántos clientes cumplen en agosto? | Número de clientes |
| ¿Quiénes cumplen años en marzo? | Lista de nombres |
| ¿Cuántos clientes tiene el líder 140255? | Número de clientes |
| ¿Quiénes son del equipo de Carolina? | Lista de nombres del equipo |
| Pedidos del cliente 141639 | Resumen con unidades y PVP |
| ¿Qué líder tuvo más pedidos? | Ranking global del líder con mayor cantidad de pedidos |
| ¿Qué campaña fue la que más PVP hizo ESTEVEZ? | Extrae "Estevez", filtra y devuelve su mejor campaña por facturación |
| ¿Qué cliente vendió más unidades? | Ranking global del cliente con más unidades compradas |
| ¿Cuantos cunplen en maio? | Autocorrige y responde correctamente |
