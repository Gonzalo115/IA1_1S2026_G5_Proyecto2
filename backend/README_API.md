# API de Detección de Rostros

## Descripción

API Flask para detectar rostros en imágenes usando OpenCV y Haar Cascades.

## Arquitectura de Capas

```
app.py (Configuración de Flask)
  ↓
routes/ (Definición de endpoints)
  ↓
controllers/ (Lógica de requests)
  ↓
services/ (Lógica de negocio - Detección de rostros)
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

## Endpoints

### 1. **GET /api/rostros/saludo**

Verifica que el módulo de detección está activo.

**Respuesta:**

```json
{
  "mensaje": "Módulo de detección de rostros activo ✅"
}
```

---

### 2. **POST /api/rostros/detectar**

Detecta rostros en una imagen.

**Parámetros:**

- `imagen` (file, requerido): La imagen a procesar (jpg, png, etc)

**Respuesta exitosa (200):**

```json
{
  "exito": true,
  "cantidad_rostros": 2,
  "rostros": [
    {
      "x": 150,
      "y": 100,
      "ancho": 100,
      "alto": 120
    },
    {
      "x": 400,
      "y": 150,
      "ancho": 95,
      "alto": 115
    }
  ],
  "mensaje": "Se detectaron 2 rostro(s)"
}
```

**Respuesta con error (400/500):**

```json
{
  "exito": false,
  "mensaje": "Descripción del error"
}
```

---

## Ejemplo de Uso con cURL

```bash
curl -X POST \
  -F "imagen=@ruta/a/imagen.jpg" \
  http://localhost:5000/api/rostros/detectar
```

## Ejemplo de Uso con Python

```python
import requests

# Detectar rostros
with open('imagen.jpg', 'rb') as f:
    files = {'imagen': f}
    response = requests.post(
        'http://localhost:5000/api/rostros/detectar',
        files=files
    )

print(response.json())
```

## Ejemplo de Uso con JavaScript/Fetch

```javascript
const formData = new FormData();
formData.append("imagen", imagenFile); // imagenFile es el File object

fetch("http://localhost:5000/api/rostros/detectar", {
  method: "POST",
  body: formData,
})
  .then((response) => response.json())
  .then((data) => console.log(data));
```

---

## Estructura de Archivos

```
backend/
├── app.py                     # Configuración de Flask
├── requirements.txt           # Dependencias
├── controllers/
│   ├── __init__.py
│   └── rostro_controller.py  # Controlador de rostros
├── routes/
│   ├── __init__.py
│   └── rostro_routes.py      # Definición de rutas
├── services/
│   ├── __init__.py
│   └── rostros.services.py   # Lógica de detección
├── middleware/               # Para futuras middleware
├── repositories/             # Para futuras bases de datos
└── README.md                 # Este archivo
```

---

## Cómo Funciona

1. El usuario envía una **imagen** al endpoint `/api/rostros/detectar`
2. El **controller** recibe la solicitud y valida la imagen
3. El **controller** llama al **service** pasando la imagen
4. El **service** utiliza OpenCV (cv2) y Haar Cascades para detectar rostros
5. El **service** retorna las coordenadas y cantidad de rostros detectados
6. El **controller** retorna el resultado en JSON al usuario

---

## Línea de Ejecución

```
request.files['imagen']
    ↓
RostroController.detectar_rostro_endpoint()
    ↓
RostrosService.detectar_rostros(imagen_array)
    ↓
cv2.CascadeClassifier.detectMultiScale()
    ↓
Retorna: {rostros: [coordenadas], cantidad_rostros: n}
    ↓
JSON Response
```

---

## Dependencias

- **Flask**: Framework web
- **Flask-CORS**: Manejo de CORS para requests desde frontend
- **opencv-python**: Visión computacional y detección de rostros
- **numpy**: Procesamiento de arrays numéricos

---

## Notas

- La detección usa **Haar Cascades** que ya aprendió a reconocer rostros
- El print "🔍 Se está detectando rostro..." aparecerá en la consola cuando se procese una imagen
- La API está lista para escalar con más modelos de detección en el futuro
