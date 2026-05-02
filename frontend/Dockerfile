# Etapa 1: construir la aplicacion React
FROM node:20-alpine AS builder

# URL del backend en produccion (se pasa al hacer docker build --build-arg)
ARG VITE_API_BASE=http://localhost:8000
ENV VITE_API_BASE=$VITE_API_BASE

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN npm run build

# Etapa 2: servir los archivos estaticos con nginx
FROM nginx:alpine

# Copiar archivos compilados al directorio de nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Configuracion de nginx: servir SPA (redirigir rutas al index.html)
RUN printf 'server {\n\
    listen 80;\n\
    server_name _;\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
    \n\
    location / {\n\
    try_files $uri $uri/ /index.html;\n\
    }\n\
    }\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80