# ¿Qué es Swagger UI?

Swagger UI es una herramienta visual (una interfaz web interactiva) que permite **ver, interactuar y probar** la API (el backend) de tu proyecto de forma gráfica, sin necesidad de escribir código adicional ni usar herramientas externas complicadas (como Postman).

Imagina que es como un "menú de restaurante" interactivo: te muestra todos los platos (rutas/endpoints) que tu servidor ofrece, qué ingredientes necesitas enviarle (parámetros) y te deja probar el plato ahí mismo.

## ¿Para qué se usa y por qué lo piden los profesores?

1. **Documentación Automática e Interactiva:** 
   A los profesores (y a la industria en general) les encanta Swagger porque elimina la necesidad de escribir manuales aburridos y estáticos. Swagger lee tu código y genera el manual automáticamente.
2. **Pruebas (Testing) Ágiles:** 
   Tiene un botón mágico llamado *"Try it out"* (Pruébalo) que te permite enviar datos reales a tu servidor desde el navegador y ver qué responde. Es súper útil para asegurar que la lógica de Python funciona antes de conectarla al HTML/JS.
3. **Contrato de Comunicación:** 
   Es el lenguaje universal. Si el día de mañana alguien más hace una aplicación móvil para tu chatbot, solo necesita mirar tu Swagger para saber cómo conectarse a tu backend.

## ¡La excelente noticia sobre FastAPI!

En muchos lenguajes o frameworks (como Node.js o Flask), agregar Swagger requiere instalar librerías adicionales engorrosas y escribir mucho código de configuración.

Sin embargo, como en nuestras reglas de arquitectura definimos utilizar **FastAPI** para el backend, ¡Swagger UI viene **incluido de fábrica y es 100% automático**! 

## ¿Cómo probarlo ahora mismo?

He creado el archivo `backend/main.py` con el código inicial de nuestro servidor FastAPI. Para ver tu Swagger funcionando, haz lo siguiente:

1. Abre una terminal en tu proyecto (la carpeta `bot204`).
2. Arranca el servidor ejecutando este comando (usando `uvicorn` que ya está en tu `requirements.txt`):
   ```bash
   uvicorn backend.main:app --reload
   ```
3. Una vez que diga que está corriendo, abre tu navegador web en las siguientes direcciones:
   - **Tu Chatbot Frontend:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/) (Aquí verás el diseño visual que creamos antes).
   - **🌟 Tu Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (Aquí verás la magia de Swagger).

*Nota: Si entras a `/docs`, verás que ya existe una ruta de prueba llamada `/api/estado`. Dale clic, presiona "Try it out" (Pruébalo), luego "Execute" (Ejecutar) y verás la respuesta de tu propio servidor.*
