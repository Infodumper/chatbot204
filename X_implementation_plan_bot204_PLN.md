# Plan de Aprendizaje para Bot204 (Basado en NLP Clásico)

Revisé tus trabajos en `C:\TGPN\CD_e_IA\PLN`, especialmente `work_practico_nlp.py` y `proceso-completo-dinamicas-1.py`. ¡Excelente trabajo con la implementación desde cero de algoritmos clásicos de NLP!

Es una gran idea integrar exactamente esas técnicas en el chatbot. En lugar de usar búsquedas rígidas de texto, vamos a construir un pipeline de **Procesamiento de Lenguaje Natural** usando tu propio código para entender las intenciones.

## Fase 1: Pipeline de NLP (Integración de tus funciones)

Actualizaremos `chat.py` para que cada mensaje del usuario pase por las siguientes etapas antes de llegar a Pandas:

1. **Limpieza y Tokenización (`nltk` y `re`):**
   - Utilizaremos tu lógica de `proceso-completo-dinamicas-1.py`: convertir a minúsculas, usar Expresiones Regulares para eliminar caracteres extraños y `nltk.word_tokenize` para separar el mensaje en palabras limpias.

2. **Autocorrección (Distancia de Levenshtein):**
   - Implementaremos la función `levenshtein_dp` de tu TP.
   - Crearemos un **Vocabulario** específico de nuestro negocio (meses, nombres de líderes, localidades, palabras como "cumpleaños", "pedidos", "clientes").
   - Si el usuario escribe mal (ej: *"¿cuantos cunplen en maio?"*), el sistema lo autocorregirá a *"¿cuantos cumplen en mayo?"* usando la distancia matemática.

3. **Categorización de Intenciones (Bag of Words):**
   - Usaremos tu sistema de `CATEGORIAS` y puntuación.
   - Definiremos categorías (intenciones) como `cumpleanos_mes`, `buscar_por_lider`, `buscar_por_localidad`.
   - El sistema le dará puntos a cada categoría basado en las palabras del usuario y elegirá la intención ganadora.

## Fase 2: Conexión de Intenciones con Pandas

Una vez que el pipeline NLP de la Fase 1 nos diga qué quiere el usuario (Categoría) y sobre qué (Entidad, ej. "mayo"), ejecutaremos la acción correspondiente:

1. **Intención `cumpleanos_mes`**: Extraemos el mes (ya autocorregido) y filtramos `clientes_limpio.csv`.
2. **Intención `buscar_por_lider`**: Extraemos el número de líder y contamos sus clientes/pedidos.
3. **Intención `buscar_por_localidad`**: Extraemos la localidad autocorregida y filtramos.

## Fase 3: Refactorización (Opcional)
Crearemos una clase `MotorNLP` dentro de `chat.py` que encapsule todas estas funciones tuyas para que quede muy profesional y modular de cara a tus profesores.

---

## User Review Required

> [!IMPORTANT]
> **Requisito de Librerías:** Tu código de ejemplo usa `nltk`. Necesitaremos asegurarnos de que `nltk` esté instalado (lo agregaremos a `requirements.txt`).
> 
> ¿Te parece bien este nuevo enfoque que reutiliza tus algoritmos de Distancia de Levenshtein y Bag of Words? Si lo apruebas, comienzo de inmediato con la Fase 1.
