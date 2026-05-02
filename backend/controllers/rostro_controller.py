import cv2
import numpy as np
from flask import request, jsonify
from services.rostros_services import RostrosService


class RostroController:
    """Controller para manejar operaciones de detección de rostros"""
    
    def __init__(self):
        self.rostros_service = RostrosService()
    
    def detectar_rostro_endpoint(self):
        """
        Endpoint para detectar rostros en una imagen
        
        Request:
            - File: 'imagen' (imagen en formato jpg, png, etc)
            
        Response:
            JSON con información de rostros detectados
        """
        try:
            # Verificar que la imagen fue enviada
            if 'imagen' not in request.files:
                return jsonify({
                    'exito': False,
                    'mensaje': 'No se envió imagen. Envía la imagen con el key "imagen"'
                }), 400
            
            archivo = request.files['imagen']
            
            if archivo.filename == '':
                return jsonify({
                    'exito': False,
                    'mensaje': 'El archivo no tiene nombre'
                }), 400
            
            # Leer la imagen del archivo
            img_array = np.frombuffer(archivo.read(), np.uint8)
            imagen = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if imagen is None:
                return jsonify({
                    'exito': False,
                    'mensaje': 'No se pudo procesar la imagen'
                }), 400
            
            # Llamar al servicio para detectar rostros
            resultado = self.rostros_service.detectar_rostros(imagen)
            
            return jsonify(resultado), 200
            
        except Exception as e:
            return jsonify({
                'exito': False,
                'mensaje': f'Error al procesar la solicitud: {str(e)}'
            }), 500


# Instancia global del controller
rostro_controller = RostroController()
