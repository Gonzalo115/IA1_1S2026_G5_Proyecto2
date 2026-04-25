# Frontend — HandTalk / detector de rostros

Cliente **React + TypeScript + Vite** que consume la API **Flask** del backend.

## Requisitos

- Node.js compatible con la versión indicada en el proyecto.
- Backend en ejecución (`python app.py` desde `backend`, puerto **5000** por defecto).

## Instalación y desarrollo

```bash
cd frontend
npm install
npm run dev
```

El servidor de desarrollo de Vite mostrará la URL local (habitualmente `http://127.0.0.1:5173`).

## Comportamiento actual

- Accede a la **cámara del navegador** y envía frames periódicos al backend.
- Llama a **`POST http://localhost:5000/api/rostros/detectar`** con el frame como archivo **`imagen`**.
- Muestra el resultado de detección de **rostros** devuelto por la API.

Si cambias el host o el puerto del backend, actualiza la URL del `fetch` en el código de la aplicación para que coincida con tu entorno.

## Scripts útiles

| Comando | Descripción |
|---------|-------------|
| `npm run dev` | Servidor de desarrollo con recarga en caliente. |
| `npm run build` | Compilación para producción. |
| `npm run preview` | Vista previa del build. |
| `npm run lint` | ESLint sobre el código fuente. |
