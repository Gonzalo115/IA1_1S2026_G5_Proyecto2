# HandTalk AI — IA1_1S2026_G5_Proyecto2

## Descripción

Sistema de reconocimiento de gestos de mano orientado a **lenguaje de señas**: captura de vídeo, detección de mano con **MediaPipe**, extracción de un vector de características fijo e inferencia con un modelo **scikit-learn**. Expone una **API REST en Flask** (detección de rostros en paralelo y endpoint de predicción por webcam del servidor). Incluye un **cliente React** opcional para pruebas con la cámara del navegador.

## Tecnologías

| Área | Tecnología |
|------|------------|
| API | **Flask**, Flask-CORS |
| Visión | **OpenCV**, **MediaPipe** (Tasks, manos) |
| ML | **scikit-learn**, **NumPy**, **joblib** |
| Cliente | **React**, TypeScript, Vite |

## Arquitectura (backend)

```
app.py                 → Aplicación Flask, CORS, instancia única de InferenceService
  ↓
routes/              → Blueprints (rostros, predicción)
  ↓
controllers/         → Validación HTTP (rostros)
services/            → Lógica de negocio (rostros Haar; captura + PredictService)
  ↓
handtalk/            → Dominio HandTalk (independiente del framework web)
  ├── inference_service.py   → MediaPipe + features + modelo + suavizado
  ├── smoother.py
  └── cv/                    → Cámara, detección, features, modelo MediaPipe (.task)
```

El modelo entrenado se espera en **`backend/models/modelo_manos.pkl`**.

## Requisitos previos

- **Python 3.11+** y `pip`
- **Node.js** (solo si usas el frontend)
- **Webcam** en el equipo donde corre el backend (necesaria para `GET /predict`)

---

## Instalación

### Windows (PowerShell)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Linux / macOS

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend (opcional)

```bash
cd frontend
npm install
```

---

## Ejecutar el backend

Desde el directorio **`backend`** con el entorno virtual activado:

```bash
python app.py
```

Por defecto el servidor escucha en **`http://127.0.0.1:5000`** (`0.0.0.0:5000` en la configuración actual).

---

## Probar el endpoint `GET /predict`

1. Arranca el backend (`python app.py`).
2. Asegúrate de que la **webcam del servidor** esté disponible y, si es posible, muestra una mano frente a la cámara.
3. Desde otra terminal o el navegador:

   ```bash
   curl http://127.0.0.1:5000/predict
   ```

**Respuestas JSON habituales:**

| Resultado | Cuerpo (ejemplo) |
|-----------|------------------|
| Predicción | `{"raw": "...", "stable": "..."}` |
| Sin frame de cámara | `{"error": "No frame captured"}` |
| Sin mano detectada | `{"error": "No hand detected"}` |

El código HTTP es **200** en todos los casos anteriores.

---

## Documentación adicional

- Guía de ejecución del backend: [`RUN_BACKEND.md`](RUN_BACKEND.md)
- Detalle de endpoints y estructura de carpetas: [`backend/README_API.md`](backend/README_API.md)
- Frontend: [`frontend/README.md`](frontend/README.md)

---

## Demo de visión (opcional, consola)

Con el entorno activado, desde `backend`:

```bash
python -m handtalk.cv.webcam_app
```

Abre una ventana con detección de manos (salir con **Q** o **ESC**).
