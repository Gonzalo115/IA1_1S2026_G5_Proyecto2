from flask import Blueprint
from controllers.rostro_controller import rostro_controller

# Crear el blueprint de rutas para rostros
rostro_bp = Blueprint('rostro', __name__, url_prefix='/api/rostros')


@rostro_bp.route('/detectar', methods=['POST'])
def detectar_rostro():
    """
    POST /api/rostros/detectar
    
    Detecta rostros en una imagen enviada
    
    Parámetros:
        - imagen (file): La imagen a procesar
    """
    return rostro_controller.detectar_rostro_endpoint()


# Ruta de prueba
@rostro_bp.route('/saludo', methods=['GET'])
def saludo():
    """GET /api/rostros/saludo - Ruta de prueba"""
    return {'mensaje': 'Módulo de detección de rostros activo'}
