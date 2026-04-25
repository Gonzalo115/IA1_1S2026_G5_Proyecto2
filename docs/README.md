# IA1_1S2026_G5_Proyecto2

## Descripcion general

- **Frontend:** aplicacion web desarrollada con React, TypeScript y Vite.
- **Backend:** API desarrollada con Flask para procesamiento de imagenes usando OpenCV.

## Tecnologias utilizadas

### Frontend

- React
- TypeScript
- Vite
- CSS
- API del navegador `navigator.mediaDevices.getUserMedia` para acceder a la camara

### Backend

- Python
- Flask
- Flask-CORS
- OpenCV
- NumPy
- Haar Cascades de OpenCV para deteccion de rostros

## Estructura del proyecto

```text
IA1_1S2026_G5_Proyecto2/
|-- backend/
|   |-- app.py
|   |-- requirements.txt
|   |-- README_API.md
|   |-- controllers/
|   |   |-- rostro_controller.py
|   |-- routes/
|   |   |-- rostro_routes.py
|   |-- services/
|       |-- rostros_services.py
|
|-- frontend/
|   |-- package.json
|   |-- vite.config.ts
|   |-- index.html
|   |-- src/
|       |-- main.tsx
|       |-- App.tsx
|       |-- App.css
|       |-- index.css
|       |-- assets/
|
|-- README.md
```

## Arquitectura general

El sistema sigue una separacion simple entre cliente web y servidor API.

![Texto alternativo](/docs/arquitectura_sistema_general.png)

## Instalacion

### Requisitos previos

Se necesita tener instalado:

- Python 3
- Node.js y npm
- Navegador web con soporte para camara

### Backend

Entrar a la carpeta del backend:

```bash
cd backend
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

### Frontend

Entrar a la carpeta del frontend:

```bash
cd frontend
```

Instalar dependencias:

```bash
npm install
```

## Ejecucion

Para usar el sistema se deben ejecutar el backend y el frontend al mismo tiempo, en terminales separadas.

### Ejecutar backend

Desde la carpeta `backend`:

```bash
python app.py
```

El backend queda disponible en:

```text
http://localhost:5000
```

Endpoints actuales:

- `GET /`
- `GET /api/rostros/saludo`
- `POST /api/rostros/detectar`

### Ejecutar frontend

Desde la carpeta `frontend`:

```bash
npm run dev
```

Vite mostrara en consola la URL local para abrir la aplicacion. Normalmente es:

```text
http://localhost:5173
```

## Uso del sistema

1. Iniciar el backend con `python app.py`.
2. Iniciar el frontend con `npm run dev`.
3. Abrir la URL del frontend en el navegador.
4. Aceptar el permiso de camara cuando el navegador lo solicite.
5. Verificar que aparezca el video de la camara.
6. El sistema enviara frames automaticamente al backend.
7. En pantalla se mostrara el estado de la camara y la cantidad de rostros detectados.
8. Para verificar el backend manualmente, se puede abrir:

```text
http://localhost:5000/api/rostros/saludo
```

## Manual tecnico

### Backend

El backend esta organizado por:

```text
app.py
  |
  v
routes/rostro_routes.py
  |
  v
controllers/rostro_controller.py
  |
  v
services/rostros_services.py
```

Responsabilidades:

- `app.py`: crea la aplicacion Flask, habilita CORS y registra las rutas.
- `routes/rostro_routes.py`: define las rutas del modulo de rostros.
- `controllers/rostro_controller.py`: recibe la solicitud HTTP, valida la imagen y prepara la respuesta.
- `services/rostros_services.py`: contiene la logica de procesamiento de imagenes con OpenCV.

### Como agregar cambios al backend

Para agregar un nuevo endpoint:

1. Crear o modificar una ruta dentro de `backend/routes/`.
2. Crear el metodo correspondiente en un controlador dentro de `backend/controllers/`.
3. Colocar la logica principal en un servicio dentro de `backend/services/`.
4. Registrar el blueprint en `app.py` si se crea un modulo nuevo.
5. Probar el endpoint desde navegador, cURL, Postman o desde el frontend.

Para cambiar el procesamiento de imagenes:

1. Revisar `backend/services/rostros_services.py`.
2. Modificar el metodo `detectar_rostros`.
3. Mantener una respuesta JSON clara para que el frontend pueda consumirla.

Formato actual de respuesta exitosa:

```json
{
  "exito": true,
  "cantidad_rostros": 1,
  "rostros": [
    {
      "x": 10,
      "y": 20,
      "ancho": 100,
      "alto": 120
    }
  ],
  "mensaje": "Se detectaron 1 rostro(s)"
}
```

### Frontend

El frontend principal esta en:

```text
frontend/src/App.tsx
```

Responsabilidades actuales:

- Solicitar acceso a la camara.
- Mostrar el video en pantalla.
- Capturar frames usando un canvas oculto.
- Enviar los frames al backend usando `fetch`.
- Mostrar el resultado de la deteccion.

### Como agregar cambios al frontend

Para modificar la vista principal:

1. Editar `frontend/src/App.tsx`.
2. Si se requiere cambiar estilos, editar `frontend/src/App.css` o `frontend/src/index.css`.
3. Ejecutar `npm run dev` y revisar los cambios en el navegador.

Para cambiar la URL del backend:

Buscar en `frontend/src/App.tsx`:

```ts
fetch("http://localhost:5000/api/rostros/detectar", {
```


## Manual de usuario

### Objetivo de la aplicacion

Permitir al usuario probar una funcionalidad inicial de reconocimiento visual desde la camara del navegador.

### Pasos de uso

1. Abrir la aplicacion web.
2. Conceder permiso de camara.
3. Ubicarse frente a la camara.
4. Esperar a que el sistema procese los frames.
5. Revisar en pantalla el mensaje de estado.
6. Observar la cantidad de rostros detectados.

## Contenerizacion

El enunciado solicita archivos `Dockerfile` y `docker-compose.yml` funcionales para desplegar el sistema.

En el estado actual del repositorio no se encontraron estos archivos. Por lo tanto, la contenerizacion queda registrada como pendiente para una siguiente iteracion.
