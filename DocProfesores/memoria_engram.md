# Memoria de Trabajo del Agente (Engram) - Historial del Proyecto Bot204

Este documento contiene el historial completo de la memoria a largo plazo que el Agente Antigravity ha guardado sobre este proyecto. La memoria registra automáticamente resúmenes de sesión, descubrimientos técnicos, patrones de código, correcciones de errores y decisiones arquitectónicas para no perder el contexto entre diferentes sesiones de trabajo.

---

## 📅 Sesión del 07/07/2026

### [Arquitectura] Major Refactoring: data_loader, buscar_entidad, HTML rendering (#2511)
**Qué se hizo**: Refactorización profunda del backend de Bot204.
**Por qué**: Para eliminar código duplicado (fix_encoding, búsqueda de Levenshtein), romper importaciones circulares entre `chat.py` y `main.py`, remover el patrón frágil `locals()`, y arreglar el renderizado HTML en el frontend.
**Dónde**: Se creó `backend/data_loader.py` (carga centralizada de CSVs). Se reescribió `backend/chat.py` (búsqueda genérica MotorNLP.buscar_entidad, separación de funciones _resolver por intención). Se limpió `backend/data_processor.py` (fix_encoding compartido). Se actualizó `backend/main.py`. Se actualizó `frontend/script.js` (innerHTML para mensajes del bot). Se renombraron y reescribieron documentos como `README.md`, `ManualUsuario.md` y `ArquitecturaTecnica.md`.
**Aprendizaje**: La terminal de Windows (cp1252) no puede imprimir marcas de verificación unicode (✓) — es mejor usar ASCII [OK]. El patrón `in locals()` es frágil; es mucho más limpio inicializar variables en `None`.

---

## 📅 Sesiones del 08/07/2026

### [Resumen de Sesión] Motor NLP y Entornos Virtuales (#2516)
**Meta**: Corregir las rutas del entorno virtual tras el renombrado del proyecto a `bot204` y expandir drásticamente el motor de NLP para soportar consultas cruzadas de Top/Ranking (filtrado por entidad + agrupación por campaña) usando Pandas.
**Descubrimientos**: 
- El tokenizador con la expresión regular `[^a-záéíóúñü0-9\s]` preserva las tildes, lo que causaba que la palabra "más" no fuera autocorregida y no hiciera match con el conjunto interno que esperaba "mas" sin tilde. Hubo que añadir palabras tildadas a las comprobaciones directas.
- El algoritmo `buscar_entidad` basado en Levenshtein es lo suficientemente flexible para extraer el nombre objetivo ("ESTEVEZ") del resto de la consulta excluyendo las stop-words del NLP.
**Logros**: Se arregló el entorno virtual, se implementó el filtrado de entidades en `chat.py` permitiendo responder cruces de datos (ej. "¿Qué campaña fue la que más PVP hizo ESTEVEZ?"), y se actualizó `ManualUsuario.md`.

### [Patrón] Parametrización de data_processor.py (#2520)
**Qué**: Se creó `anonymize_csv.py` para mezclar nombres y generar DNIs/teléfonos falsos, y se modificó `clean_clientes` y `clean_pedidos` en `data_processor.py` para aceptar nombres de archivos de entrada/salida.
**Por qué**: Se necesitaba trabajar con datos falsos sin romper las estructuras de datos existentes, y el procesador requería flexibilidad.
**Aprendizaje**: Modificar el procesador para aceptar argumentos lo hace reusable para probar datasets sin tener nombres de archivo duros en el código.

### [Resumen de Sesión] Base de Datos Anónima (#2521)
**Meta**: Crear versiones anonimizadas de los datasets de clientes y pedidos para trabajar de forma segura con datos falsos.
**Logros**: Se creó `anonymize_csv.py` para aleatorizar nombres y números. Se procesaron y generaron `clientes2.csv` y `pedidos2.csv` (crudos y limpios), parametrizando con éxito el flujo de limpieza para el futuro.

---

## 📅 Sesiones del 14/07/2026

### [Resumen de Sesión] Race Condition y Primer Release (Beta 1) (#2540)
**Meta**: Configurar la aplicación, solucionar un problema de inicio (race condition) entre FastAPI y Streamlit, y realizar el primer release (beta 1).
**Descubrimientos**: Streamlit intentaba cargar la UI antes de que el servidor FastAPI estuviera listo en el puerto 8000, lo que resultaba en "Connection Refused".
**Logros**: Se solucionó implementando active polling al endpoint `/api/estado` en el hilo principal antes de renderizar la UI de Streamlit (esperando hasta 10 segundos). Se subió la versión "beta 1".

### [Bugfix] Fixed connection refused error on startup (#2539)
**Qué**: Se incrementó el tiempo de espera de inicio para FastAPI en la app de Streamlit.
**Aprendizaje**: Los sleep timers programados estáticamente (ej. `time.sleep(1)`) para la inicialización del backend son propensos a race conditions. Es mucho más robusto esperar activamente a que un endpoint de API responda con 200 OK.

### [Resumen de Sesión] Estética, NLP y Swagger (#2538)
**Meta**: Ajustes estéticos finales de Bot204 y clarificación del funcionamiento de NLP y Swagger.
**Descubrimientos**: El NLP retorna correctamente las respuestas de respaldo ("Entendí que buscas los pedidos de un líder...") cuando la entidad no existe en los CSVs. Swagger opera automáticamente de fondo con FastAPI.
**Logros**: Se eliminaron iconos laterales de la UI. Se aplicaron los temas corporativos Kaizuna (modo oscuro azul y claro blanco) en `style.css` de manera estricta y sin gradientes distractores.

### [Resumen de Sesión] Reinicio de Repositorio (#2541)
**Meta**: Reiniciar el repositorio en GitHub "desde cero" con un `.gitignore` limpio.
**Descubrimientos**: El archivo `.gitignore` antiguo tenía duplicados y reglas redundantes que se unificaron (ej. `clientes_colores*.png`).
**Logros**: Repositorio limpiado, unificado a la URL remota de origen `chatbot204.git` y subido a la rama main.

### [Arquitectura] Optimización y Documentación Completa (#2544)
**Qué**: Añadidos docstrings al backend y reescritura total de `README.md`, `ManualUsuario.md` y `ArquitecturaTecnica.md`.
**Por qué**: Reflejar el estado actual (autenticación `auth.py`, login modal, barra lateral, tema claro/oscuro) que no figuraba en los docs.
**Aprendizaje**: El ManualUsuario resultó el documento más exhaustivo. El README para guías rápidas y ArquitecturaTécnica para flujo de datos y división de responsabilidades.

### [Resumen de Sesión] Mejoras al Motor NLP (#2548)
**Meta**: Mejorar la lógica y robustez del NLP para búsquedas, filtros temporales y manejo de contexto conversacional.
**Descubrimientos**: Gemini se negaba a redactar si Pandas le pasaba todo el dataset sin filtrar cuando se pedía un mes sin año. El CSS `text-fit: grow` probó ser la mejor herramienta nativa sin JS para ajustar fuentes dinámicamente.
**Logros**: Se implementó herencia de contexto (`USER_CONTEXT`) en `chat.py` para permitir consultas de seguimiento (ej. "¿Y en Abril?"). Limpieza de credenciales.

---

## 📅 Sesión del 16/07/2026

### [Resumen de Sesión] UI de Sesiones y Saludos Dinámicos (#2554)
**Meta**: Implementar un saludo personalizado en el chatbot e incorporar la funcionalidad para borrar historiales de consultas sin alterar el ID/número de las restantes.
**Descubrimientos**: Si el CSS o JS se queda guardado en caché, los modales fallan al no detectar las clases nuevas. Solucionado usando "cache busters" (ej. `?v=7`). Para que no se rompan las listas al borrar sesiones, el ID numérico debe basarse en el número máximo existente (no en el tamaño del array).
**Logros**: Backend y Frontend unificados para el manejo de sesiones con el nombre de usuario dinámico. Botón y modal personalizado de borrado creados con éxito respetando colores corporativos Kaizuna.
