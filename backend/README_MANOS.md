# API de Detección de Rostros y Señas de Mano

## Descripción

API Flask para detectar rostros e identificar señas de mano usando OpenCV, Haar Cascades y MediaPipe con Machine Learning.

## Arquitectura de Capas

```
app.py (Configuración de Flask)
  ├─ routes/rostro_routes.py (Rutas de rostros)
  │   └─ controllers/rostro_controller.py
  │       └─ services/rostros_services.py
  │
  └─ routes/mano_routes.py (Rutas de manos)
      ├─ controllers/mano_controller.py
      │   └─ services/mano_services.py
      │
      └─ controllers/entrenamiento_controller.py
          └─ services/entrenamiento_services.py
```

## Instalación

1. **Instalar dependencias:**

```bash
pip install -r requirements.txt
```

2. **Ejecutar la API:**

```bash
python app.py
```

La API estará disponible en `http://localhost:5000`

---

## 📊 Estructura del Dataset

Para entrenar el modelo, organiza tus imágenes así:

```
data/
├── 1/
│   ├── imagen1.jpg
│   ├── imagen2.jpg
│   └── ...
├── 2/
│   ├── imagen1.jpg
│   ├── imagen2.jpg
│   └── ...
├── 3/
│   └── ...
...
└── 10/
    └── ...
```

Cada carpeta representa una seña (1-10).

---

## 🔴 Endpoints de Rostros

### 1. **GET /api/rostros/saludo**

Verifica que el módulo de detección de rostros está activo.

**Respuesta:**

```json
{
  "mensaje": "Módulo de detección de rostros activo ✅"
}
```

### 2. **POST /api/rostros/detectar**

Detecta rostros en una imagen.

**Parámetros:**

- `imagen` (file, requerido): La imagen a procesar

**Respuesta exitosa (200):**

```json
{
  "exito": true,
  "cantidad_rostros": 2,
  "rostros": [
    { "x": 150, "y": 100, "ancho": 100, "alto": 120 },
    { "x": 400, "y": 150, "ancho": 95, "alto": 115 }
  ],
  "mensaje": "Se detectaron 2 rostro(s)"
}
```

---

## ✋ Endpoints de Manos

### 1. **GET /api/manos/saludo**

Verifica que el módulo de manos está activo.

**Respuesta:**

```json
{
  "mensaje": "Módulo de detección de manos activo ✅",
  "endpoints": {
    "analizar": "POST /api/manos/analizar",
    "entrenar": "POST /api/manos/entrenar"
  }
}
```

### 2. **POST /api/manos/entrenar** 🤖

Entrena el modelo con imágenes del dataset.

**Parámetros (opcionales):**

- `ruta_dataset` (form): Ruta a la carpeta del dataset (default: "data")

**Respuesta exitosa (200):**

```json
{
  "exito": true,
  "mensaje": "Modelo entrenado exitosamente",
  "accuracy": 0.95,
  "total_muestras": 500,
  "muestras_entrenamiento": 350,
  "muestras_prueba": 150,
  "etiquetas": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
  "reporte": {
    "1": {"precision": 0.95, "recall": 0.92, "f1-score": 0.93},
    ...
  }
}
```

### 3. **POST /api/manos/analizar** 📷

Analiza una imagen y predice la seña de mano.

**Parámetros:**

- `imagen` (file, requerido): Imagen con una mano

**Respuesta exitosa (200):**

```json
{
  "exito": true,
  "prediccion": "5",
  "confianza": 0.94,
  "confianzas_por_clase": {
    "1": 0.02,
    "2": 0.01,
    "3": 0.01,
    "4": 0.02,
    "5": 0.94,
    ...
  },
  "mensaje": "Seña detectada: 5",
  "manos_detectadas": 1
}
```

**Respuesta cuando no se detecta mano (400):**

```json
{
  "exito": false,
  "prediccion": null,
  "confianza": null,
  "mensaje": "No se detectó mano en la imagen",
  "manos_detectadas": 0
}
```

---

## 📝 Ejemplos de Uso

### Entrenar modelo con cURL

```bash
curl -X POST http://localhost:5000/api/manos/entrenar
```

### Analizar imagen con cURL

```bash
curl -X POST \
  -F "imagen=@seña.jpg" \
  http://localhost:5000/api/manos/analizar
```

### Python

```python
import requests

# Entrenar
response = requests.post('http://localhost:5000/api/manos/entrenar')
print(response.json())

# Analizar
with open('seña.jpg', 'rb') as f:
    files = {'imagen': f}
    response = requests.post(
        'http://localhost:5000/api/manos/analizar',
        files=files
    )
print(response.json())
```

### JavaScript/Fetch

```javascript
// Entrenar
fetch("http://localhost:5000/api/manos/entrenar", {
  method: "POST",
})
  .then((r) => r.json())
  .then((data) => console.log(data));

// Analizar
const formData = new FormData();
formData.append("imagen", imagenFile);

fetch("http://localhost:5000/api/manos/analizar", {
  method: "POST",
  body: formData,
})
  .then((r) => r.json())
  .then((data) => console.log(data));
```

---

## 🔍 Flujo de Funcionamiento

### Entrenamiento:

```
POST /api/manos/entrenar
    ↓
EntrenaciontoController.entrenar_endpoint()
    ↓
EntrenaciontoService.entrenar_modelo("data")
    ↓
1. Leer imágenes de las carpetas 1-10
2. Procesar cada imagen con MediaPipe Hands
3. Extraer 21 landmarks (63 valores: x, y, z)
4. Entrenar RandomForestClassifier con 100 árboles
5. Guardar modelo en "modelo_manos.pkl"
    ↓
Retorna: {accuracy, reporte, etiquetas}
```

### Predicción:

```
POST /api/manos/analizar
    ↓
ManoController.analizar_mano_endpoint()
    ↓
ManoService.analizar_imagen(imagen)
    ↓
1. Procesar imagen con MediaPipe Hands
2. Extraer landmarks de la mano detectada
3. Usar modelo.predict() para clasificar
4. Retornar predicción y confianza
    ↓
JSON Response
```

---

## 📦 Dependencias

- **Flask**: Framework web
- **Flask-CORS**: Manejo de CORS
- **opencv-python**: Visión computacional
- **numpy**: Procesamiento de arrays
- **mediapipe**: Detección de manos con ML
- **scikit-learn**: Modelos de Machine Learning
- **joblib**: Serialización de modelos

---

## ⚙️ Configuración

### Variables de entorno

```bash
FLASK_ENV=development
FLASK_DEBUG=True
```

### Ejecución

```bash
python app.py
```

La API se ejecuta en:

- **Host**: 0.0.0.0
- **Puerto**: 5000
- **Modo Debug**: True

---

## 📊 Notas Importantes

1. **Entrenamiento**: Requiere estar en la carpeta raíz del backend donde esté la carpeta `data/`
2. **Modelo**: Se guarda como `modelo_manos.pkl` en la raíz del backend
3. **MediaPipe**: Detecta automáticamente manos en cualquier ángulo
4. **Confianza**: Valor entre 0 y 1, más cerca de 1 es más preciso
5. **Línea del comando**: Los prints se muestran en la consola del backend (ej: "🔍 Se está detectando seña de mano...")

---

## 🚀 Próximos Pasos

- Agregar almacenamiento de historial de predicciones
- Implementar fine-tuning del modelo
- Agregar soporte para múltiples manos
- Crear dashboard de estadísticas
- Exportar modelo a TensorFlow Lite para mobile
