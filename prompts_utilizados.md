# Prompts Utilizados en el Desarrollo

Para el Trabajo Práctico, aquí se documentan los prompts enviados al agente (OpenCode / Gemini) para ir construyendo el proyecto paso a paso:

### Prompt 1: Limpieza avanzada de Clientes
> "Hola. Necesito que actualices el script de Python (`data_processor.py`) usando Pandas para limpiar el archivo `datos_originales/clientes.csv`. 
> Aplica los siguientes requerimientos:
> 1. Crea la carpeta `datos_limpios` si no existe.
> 2. Carga el CSV original.
> 3. Reemplaza los textos 'NULL' por nulos reales. Rellena las localidades vacías con 'Desconocido'.
> 4. Corrige **TODOS los errores de codificación** en los nombres (por ejemplo, transformar 'ACUÃ‘A CELINA' en 'ACUÑA CELINA') y **quita los espacios que sobran** al principio y al final en las columnas de texto principales (Cliente, Localidad, Dirección, Email).
> 5. Unifica las columnas de nombres (`Cliente` y `Nombre_Clip`) dando prioridad a `Cliente`, elimina `Nombre_Clip` y luego formatea la columna `Cliente` a **todas MAYÚSCULAS**.
> 6. Busca filas duplicadas utilizando el criterio: **Si Nro, Cliente y Lider son iguales**, considera que es un duplicado y **borra el más antiguo** (conserva solo el último registro).
> 7. Formatea la columna `Email` para que quede completamente en **minúsculas**.
> 8. Unifica las columnas de teléfonos (`Telefono_Perla` y `Telefono_Clip`) en una sola columna nueva llamada `Telefono`.
> 9. Unifica las fechas de nacimiento (`FecNac_Perla` y `FecNac_Clip`) en una sola columna llamada `FecNac`.
> 10. Elimina las columnas `IdCliente` e `IdClip` unificando el identificador en una nueva columna llamada `Id` que sea autoincrementable.
> 11. Guarda el resultado en `datos_limpios/clientes_limpio.csv` (formato utf-8) sin alterar el archivo original. Recordatorio: NO uses SQLite."

### Prompt 2: Optimización de la base de datos (Normalización de Líderes)
> "Como paso adicional para optimizar la estructura de los datos limpios y corregir la inconsistencia de los líderes:
> 1. Crea un nuevo dataframe a partir de los clientes que contenga los códigos de líderes (`Lider`) únicos. 
> 2. Este nuevo dataframe debe tener las columnas `IdLider` (autoincremental), `Lider` (el código original) y `NombreLider`. **Asegúrate de que la columna Lider se guarde como número entero, sin decimales.**
> 3. Para obtener el `NombreLider` correcto, debes cruzar el código de `Lider` buscando ese mismo código en la columna `Nro` del dataframe de clientes (ya que cada líder es en realidad un cliente). Una vez encontrado el cliente correspondiente, copia solo la primera palabra de su columna `Cliente` y asígnala a `NombreLider`.
> 4. Guárdalo como un nuevo archivo `datos_limpios/lideres.csv`.
> 5. Una vez hecho esto, elimina la columna `NombreLider` del dataframe original de clientes (ya que ahora estarán relacionados por el código de `Lider`) y sobreescribe `clientes_limpio.csv`."

### Prompt 5: Mejoras en el Motor NLP para listar líderes
> "Por favor, mejora el archivo `chat.py` del motor NLP para soportar correctamente consultas del tipo '¿Qué líderes hay?', 'Dime los nombres de los líderes', etc.:
> 1. Agrega las palabras 'lideres', 'líderes', 'nombres', 'lista', 'todos', 'dime', 'decime', 'que', 'qué' y 'hay' al `VOCABULARIO` para que la autocorrección las reconozca.
> 2. Agrega la versión en plural de líder a la intención `buscar_lider`.
> 3. Modifica la lista `_PALABRAS_LISTADO` incorporando 'que', 'qué', 'hay', 'nombres', 'lista', 'todos', 'dime', 'decime'.
> 4. Actualiza la función `_resolver_lider()` de modo que, si el usuario pide una lista y no especifica un número de líder, se conecte a `lideres.csv` y devuelva un listado formateado con todos los líderes registrados (NombreLider)."

### Prompt 3: Limpieza de Pedidos
> "Hola. Ahora necesito que agregues una función `clean_pedidos()` al script `data_processor.py` para limpiar el archivo `datos_originales/pedidos.csv`.
> Aplica los siguientes requerimientos:
> 1. Rellena los valores 'NULL' o vacíos de `Localidad` y `Provincia` con 'Desconocido'.
> 2. Rellena los valores 'NULL' o vacíos de `IdEnvio` con -1 y `Precio_Envio` con 0.0.
> 3. Aplica la misma corrección de codificación (caracteres extraños) que hicimos en clientes para las columnas `Nombre` y `Nombre_Lider`.
> 4. Quita los espacios sobrantes al principio y al final (trim) de las columnas de texto principales (`Nombre`, `Nombre_Lider`, `Rango`, `Localidad`, `Provincia`).
> 5. Pasa los nombres (`Nombre` y `Nombre_Lider`) a MAYÚSCULAS.
> 6. **Regla de Negocio Crítica**: Elimina los pedidos duplicados **solo si coinciden exactamente en Campaña, Nro (cliente) y Lider** (conservando el último). Es muy importante incluir el `Lider` en esta validación porque un cliente puede hacer pedidos bajo distintos líderes a lo largo del tiempo, y queremos conservar su historial completo sin perder información.
> 7. Elimina la columna `Nombre_Lider` del dataframe ya que es redundante (el nombre del líder ya está normalizado en `lideres.csv` y podemos relacionarlo mediante la columna `Lider`).
> 8. Guarda el resultado en `datos_limpios/pedidos_limpio.csv` y asegúrate de que el script principal ejecute tanto la limpieza de clientes como la de pedidos."

### Prompt 4: Completar Operaciones de Preparación de Datos
> "Hola. Para cumplir estrictamente con los 8 requerimientos de la consigna sobre preparación de datos, necesito que agregues lo siguiente al script `data_processor.py`:
> 1. **Cambio de formato de fechas**: Asegúrate de que, luego de unificar la fecha de nacimiento (`FecNac`), se convierta toda la columna al formato estándar internacional `YYYY-MM-DD` usando `pd.to_datetime()`.
> 2. **Agrupamientos (groupby) y Columnas Calculadas**: En la limpieza de pedidos, extrae el Año y Orden de la Campaña numéricamente para crear nuevas columnas. Luego agrupa (`groupby`) el dataframe por número de cliente (`Nro`) y calcula dos métricas: el conteo de pedidos (`Total_Pedidos`) y la suma total gastada (`Total_Facturado`).
> 3. **Unión (merge)**: En la limpieza de clientes, recibe esas estadísticas agrupadas y haz una unión (`merge` tipo left join) para incorporar el histórico de ventas directamente al dataframe de clientes. Rellena con 0 los valores nulos generados.
> Esto complementa las operaciones de limpieza (duplicados, nulos, tipos de datos, ordenamiento) garantizando que todas las técnicas de Pandas requeridas estén implementadas y documentadas."
