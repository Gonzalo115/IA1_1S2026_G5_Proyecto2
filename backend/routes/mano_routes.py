from flask import Blueprint
from controllers.mano_controller import mano_controller
from controllers.entrenamiento_controller import entrenamiento_controller

# Crear el blueprint de rutas para manos
mano_bp = Blueprint('mano', __name__, url_prefix='/api/manos')

"""
@mano_bp.route('/analizar', methods=['POST'])
def analizar_mano():
    """
    POST /api/manos/analizar
    
    Analiza una seña de mano en una imagen
    
    Parámetros:
        - imagen (file): La imagen con la mano
    """
    return mano_controller.analizar_mano_endpoint()
"""

@mano_bp.route('/entrenar', methods=['POST'])
def entrenar_modelo():
    """
    POST /api/manos/entrenar
    
    Entrena el modelo con imágenes del dataset
    Las imágenes deben estar en carpeta 'data' con subcarpetas de clasificaciones
    
    Parámetros (opcionales):
        - ruta_dataset (form): Ruta a la carpeta del dataset (default: "data")
    """
    return entrenamiento_controller.entrenar_endpoint()


@mano_bp.route('/saludo', methods=['GET'])
def saludo():
    """GET /api/manos/saludo - Ruta de prueba"""
    return {
        'mensaje': 'Módulo de detección de manos activo',
        'endpoints': {
            'analizar': 'POST /api/manos/analizar',
            'entrenar': 'POST /api/manos/entrenar'
        }
    }
