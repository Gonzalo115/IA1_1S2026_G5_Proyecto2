from flask import Blueprint
from controllers.entrenamiento_controller import entrenamiento_controller

# Crear el blueprint de rutas para entrenars
entrenar_bp = Blueprint('entrenar', __name__, url_prefix='/api/entreanar')

@entrenar_bp.route('/', methods=['POST'])
def entrenar_modelo():
    """
    POST /api/entrenars/entrenar
    
    Entrena el modelo con imágenes del dataset
    Las imágenes deben estar en carpeta 'data' con subcarpetas de clasificaciones
    
    Parámetros (opcionales):
        - ruta_dataset (form): Ruta a la carpeta del dataset (default: "data")
    """
    return entrenamiento_controller.entrenar_endpoint()


@entrenar_bp.route('/saludo', methods=['GET'])
def saludo():
    """GET /api/entrenars/saludo - Ruta de prueba"""
    return {
        'mensaje': 'Módulo de detección de entrenars activo',
        'endpoints': {
            'entrenar': 'POST /api/entrenars/entrenar'
        }
    }
