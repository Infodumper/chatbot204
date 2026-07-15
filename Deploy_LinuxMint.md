# Guía de Despliegue en Linux Mint

Esta guía te ayudará a configurar, ejecutar y acceder a **Bot204** desde una computadora con Linux Mint (o distribuciones similares basadas en Ubuntu/Debian), y te explicará cómo acceder a la interfaz desde otra computadora en la misma red.

---

## 1. Instalación y Configuración del Servidor

### Paso 1: Preparar el entorno
Abre tu terminal (`Ctrl + Alt + T`) y asegúrate de tener instalados Python 3, `pip`, el módulo de entornos virtuales y Git:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-full git -y
```

### Paso 2: Clonar el repositorio
Descarga el código del proyecto desde GitHub y entra a la carpeta:
```bash
git clone https://github.com/Infodumper/chatbot204.git
cd chatbot204
```

### Paso 3: Crear y activar el Entorno Virtual
Es importante aislar las librerías del proyecto. Para ello crea un entorno virtual:
```bash
# Crear el entorno virtual llamado "venv"
python3 -m venv venv

# Activar el entorno virtual
source venv/bin/activate
```
*(Deberás ver `(venv)` al inicio de la línea en tu terminal).*

### Paso 4: Instalar las dependencias
Instala las librerías necesarias del proyecto (`fastapi`, `pandas`, `uvicorn`, etc.):
```bash
pip install -r requirements.txt
```

### Paso 5: Configurar las Variables de Entorno
Copia el archivo de ejemplo para crear tu configuración real:
```bash
cp .env.example .env
nano .env
```
Dentro de `nano`, pega tu clave de **Google Gemini** en `GEMINI_API_KEY` y configura tus usuarios y contraseñas.
Guarda con `Ctrl + O` (luego `Enter`) y sal con `Ctrl + X`.

---

## 2. Ejecutar el Servidor

Para que el servidor esté disponible no solo en tu computadora local, sino **para cualquier dispositivo en tu red**, debes iniciarlo especificando el host `0.0.0.0`:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
- `--host 0.0.0.0`: Le dice al servidor que escuche en todas las interfaces de red (Ethernet, Wi-Fi), no solo en `localhost`.
- `--port 8000`: El puerto donde se levantará la aplicación.

*(Para detener el servidor en cualquier momento, presiona `Ctrl + C` en esa terminal).*

---

## 3. Acceder desde otra PC (en la misma red)

Para que otra computadora o teléfono móvil pueda ver la página web del bot, ambas deben estar conectadas al mismo router (por Wi-Fi o cable). 

### Paso 1: Averiguar la IP de la computadora con Linux Mint
En la computadora donde está corriendo el bot, abre una nueva terminal y ejecuta:
```bash
hostname -I
```
Esto te devolverá algo como: `192.168.1.55 10.0.0.2`. La primera suele ser tu IP local (ej. `192.168.1.55`).

*(Alternativamente, puedes usar el comando `ip a` y buscar la dirección bajo `eth0` o `wlan0`).*

### Paso 2: Abrir el puerto en el Firewall (Opcional)
Si Linux Mint tiene el firewall activado por defecto (UFW), necesitas permitir el tráfico por el puerto 8000:
```bash
sudo ufw allow 8000/tcp
```

### Paso 3: Ingresar desde la otra PC
Ve a la otra computadora (o a un celular), abre tu navegador web (Chrome, Firefox, Safari) y en la barra de direcciones escribe la IP que obtuviste en el Paso 1, seguida de `:8000`.

**Ejemplo:**
```text
http://192.168.1.55:8000
```

¡Eso es todo! Deberías ver la pantalla de Login del Bot204 cargando perfectamente en el navegador remoto.
