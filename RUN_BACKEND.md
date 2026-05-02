# Cómo ejecutar el backend (HandTalk AI)

## 1. Resumen del proyecto

El **backend** es una API **Flask** que sirve detección de rostros (`/api/rostros/...`) y predicción de gestos de mano con **`GET /predict`** (usa la webcam del **equipo donde corre el servidor**, MediaPipe, features fijas y un modelo **scikit-learn** cargado desde disco).

---

## 2. Requisitos

| Requisito | Detalle |
|-------------|---------|
| **Python** | **3.11** (recomendado; misma familia que el proyecto). |
| **pip** | Gestor de paquetes de Python. |
| **Entorno virtual (venv)** | Aisla dependencias del sistema y del proyecto. |

Además, para **`GET /predict`**: webcam accesible en el servidor y el fichero **`backend/models/modelo_manos.pkl`** presente.

---

## 3. Configuración y arranque

Todos los comandos asumen que estás en la raíz del repositorio y entras en la carpeta **`backend`**.

### Windows (PowerShell)

**1. Crear el entorno virtual**

```powershell
cd backend
python -m venv venv
```

**2. Activar el entorno virtual**

```powershell
.\venv\Scripts\Activate.ps1
```

Si la ejecución de scripts está restringida:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**3. Instalar dependencias**

```powershell
pip install -r requirements.txt
```

**4. Arrancar la API Flask**

```powershell
python app.py
```

El servidor queda en **`http://127.0.0.1:5000`** (según la configuración de `app.py`).

**5. Desactivar el entorno (cuando termines)**

```powershell
deactivate
```

---

### Linux / macOS

**1. Crear el entorno virtual**

```bash
cd backend
python3 -m venv venv
```

**2. Activar el entorno virtual**

```bash
source venv/bin/activate
```

**3. Instalar dependencias**

```bash
pip install -r requirements.txt
```

**4. Arrancar la API Flask**

```bash
python app.py
```

**5. Desactivar el entorno**

```bash
deactivate
```

---

## 4. Probar la API: `GET /predict`

### Qué hace el endpoint

- **`GET /predict`** abre la webcam (una lectura por petición en el flujo actual), obtiene un frame, ejecuta el pipeline HandTalk (MediaPipe → vector de features → modelo → suavizado) y devuelve **JSON**.

### Formato de respuesta

Siempre se responde con **HTTP 200** y cuerpo **JSON**:

| Situación | Cuerpo |
|-----------|--------|
| Éxito | `{"raw": <etiqueta>, "stable": <etiqueta>}` — tipos según el modelo (p. ej. cadena o número). |
| No se pudo leer la cámara | `{"error": "No frame captured"}` |
| No hay mano en el frame | `{"error": "No hand detected"}` |

### Ejemplo con `curl`

Con el backend en marcha:

```bash
curl http://127.0.0.1:5000/predict
```

Comprueba también el estado general:

```bash
curl http://127.0.0.1:5000/
```

---

## 5. Solución de problemas

### La cámara no funciona o `No frame captured`

- Comprueba que la **webcam esté conectada** y no la use otra aplicación en exclusiva.
- Ejecuta el backend en la **misma máquina** donde está la cámara (el endpoint usa OpenCV en el servidor, no el navegador del cliente).
- En **Linux**, revisa permisos de dispositivo de vídeo (`/dev/video*`) y que el usuario pertenezca al grupo adecuado (p. ej. `video`).
- En **VM o servidor sin cámara**, `GET /predict` no podrá capturar frame: es el comportamiento esperado.

### Modelo no encontrado o error al arrancar

- El modelo por defecto es **`backend/models/modelo_manos.pkl`** (ruta relativa a la carpeta `backend`).
- Si falta el fichero, **`InferenceService`** fallará al crear la app y el servidor no arrancará. Coloca el `.pkl` entrenado en esa ruta o ajusta la ruta en el código de **`InferenceService`** si tu despliegue usa otra ubicación.

### Dependencias faltantes o `ModuleNotFoundError`

- Activa siempre el **venv** antes de instalar o ejecutar.
- Vuelve a instalar:

  ```bash
  pip install -r requirements.txt
  ```

- Comprueba coherencia de versión de **Python** (3.11 recomendado).

### Otros

- Más detalle de endpoints y arquitectura: **`backend/README_API.md`**.
- El stack del backend es **Flask**; no se usa FastAPI en este proyecto.
