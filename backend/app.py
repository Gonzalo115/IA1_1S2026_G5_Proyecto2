from flask import Flask
from flask_cors import CORS
from routes.rostro_routes import rostro_bp
from routes.mano_routes import mano_bp

# Crear instancia de Flask
app = Flask(__name__)

# Configurar CORS para permitir requests desde el frontend
CORS(app)

# Registrar blueprints (rutas)
app.register_blueprint(rostro_bp)
app.register_blueprint(mano_bp)


@app.route('/', methods=['GET'])
def inicio():
    """Ruta de inicio - Verificar que el servidor está activo"""
    return {
        'mensaje': 'API de Detección de Rostros y Manos activa',
        'endpoints': {
            'rostros': {
                'detectar_rostro': 'POST /api/rostros/detectar (enviar imagen)',
                'saludo': 'GET /api/rostros/saludo'
            },
            'manos': {
                'analizar_mano': 'POST /api/manos/analizar (enviar imagen)',
                'entrenar_modelo': 'POST /api/manos/entrenar',
                'saludo': 'GET /api/manos/saludo'
            }
        }
    }


if __name__ == '__main__':
    # Ejecutar en modo desarrollo
    app.run(debug=True, host='0.0.0.0', port=5000)
