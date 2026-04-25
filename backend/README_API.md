# API HandTalk / Backend Flask

## Descripción

Servidor **Flask** que expone:

- Detección de **rostros** en imágenes (OpenCV + Haar Cascades).
- Predicción de **gestos de mano** vía webcam del servidor (`GET /predict`), usando el módulo **HandTalk** (MediaPipe, features, modelo entrenado y suavizado de etiquetas).

## Arquitectura

```
app.py                    # Aplicación Flask, CORS, registro de blueprints,
                          # ruta GET /, instancia única de InferenceService
    ↓
routes/                 # Blueprints y rutas HTTP
    ├── rostro_routes   →  controllers/  →  services/rostros_services
    └── predict_routes  →  services/predict_service  (usa InferenceService)
    ↓
handtalk/               # Dominio HandTalk (independiente del framework web)
    ├── cv/             # Cámara, detección de manos (MediaPipe), features, dibujo
    ├── inference_service.py
    └── smoother.py
```

| Capa | Rol |
|------|-----|
| **`app.py`** | Crea `Flask`, habilita CORS, instancia **`InferenceService`** una sola vez, registra **`PredictService`** en `app.extensions`, registra blueprints y define `GET /`. |
| **`routes/`** | Blueprints: prefijo `/api/rostros` (rostros) y rutas de predicción (`GET /predict`). |
| **`controllers/`** | Validación y orquestación HTTP para **rostros** (no se usa en la ruta de predicción). |
| **`services/`** | Lógica de negocio: detección de rostros; captura de frame + delegación a **`InferenceService`**. |
| **`handtalk/cv/`** | Visión: `WebcamCapture`, `HandDetector` (MediaPipe Tasks), extracción de vector de features fijo, utilidades de dibujo. |

El modelo sklearn por defecto se espera en **`models/modelo_manos.pkl`** (ruta relativa a la carpeta `backend`). El modelo MediaPipe de manos se resuelve con `handtalk/cv/model_path.py` (descarga automática la primera vez si aplica).

## Instalación

```bash
cd backend
pip install -r requirements.txt
```

## Ejecución

```bash
cd backend
python app.py
```

Servidor por defecto: **`http://0.0.0.0:5000`** (acceso local típico: `http://127.0.0.1:5000`).

## Endpoints

### `GET /`

Comprueba que la API está activa y lista rutas útiles.

**Respuesta (JSON):** objeto con `mensaje` y `endpoints` (claves descriptivas y rutas).

---

### `GET /api/rostros/saludo`

Comprueba que el submódulo de rostros responde.

**Respuesta (JSON):**

```json
{
  "mensaje": "Módulo de detección de rostros activo"
}
```

---

### `POST /api/rostros/detectar`

Detecta rostros en una imagen enviada en **multipart**.

**Formulario:** campo de archivo **`imagen`** (JPEG, PNG, etc.).

**Respuesta exitosa:** JSON con `exito`, `cantidad_rostros`, `rostros` (lista de rectángulos `x`, `y`, `ancho`, `alto`) y `mensaje`.

**Errores:** JSON con `exito: false` y `mensaje`; códigos HTTP 400 o 500 según el caso.

---

### `GET /predict`

Captura **un frame** de la webcam del **equipo donde corre el servidor**, ejecuta el pipeline HandTalk (MediaPipe → features → modelo → suavizado) y devuelve el resultado.

**Respuestas (JSON):**

| Situación | Cuerpo |
|-----------|--------|
| Predicción válida | `{"raw": "<etiqueta>", "stable": "<etiqueta>"}` (tipos según el modelo). |
| Sin frame de cámara | `{"error": "No frame captured"}` |
| Sin mano detectada | `{"error": "No hand detected"}` |

Las respuestas se envían con código HTTP **200** y cuerpo JSON (incluidos los objetos con `error`).

---

## Estructura de carpetas (backend)

```
backend/
├── app.py
├── requirements.txt
├── models/
│   └── modelo_manos.pkl          # Modelo sklearn (debe existir para /predict)
├── controllers/
│   └── rostro_controller.py
├── routes/
│   ├── rostro_routes.py
│   └── predict_routes.py
├── services/
│   ├── rostros_services.py
│   └── predict_service.py
└── handtalk/
    ├── inference_service.py
    ├── smoother.py
    └── cv/
        ├── camera.py
        ├── hand_detection.py
        ├── features.py
        ├── landmark_drawing.py
        ├── model_path.py
        └── webcam_app.py          # Demo por consola (opcional)
```

## Dependencias principales

- **Flask**, **Flask-CORS**: API HTTP.
- **OpenCV**: imágenes, webcam, Haar Cascades (rostros).
- **MediaPipe**: detección de manos (Tasks API).
- **NumPy**, **scikit-learn**, **joblib**: features y modelo.

## Notas

- **`GET /predict`** depende de que exista **webcam en el servidor** y del fichero **`models/modelo_manos.pkl`**.
- El cliente frontend que envía imágenes por POST usa **`POST /api/rostros/detectar`**; no es el mismo flujo que **`GET /predict`**.
