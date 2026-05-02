import cv2
import numpy as np
from flask import request, jsonify
from services.mano_services import ManoService

class ManoController:
    """Controller para manejar detección de manos"""
    
    def __init__(self):
        self.mano_service = ManoService()
    
    def analizar_mano_endpoint(self):
        """
        Endpoint para analizar seña de mano en una imagen
        
        POST /api/manos/analizar
        
        Request:
            - File: 'imagen' (imagen con una mano)
            
        Response:
            JSON con predicción de la seña
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
            
            # Llamar al servicio para analizar
            resultado = self.mano_service.analizar_imagen(imagen)
            
            if resultado['exito']:
                return jsonify(resultado), 200
            else:
                return jsonify(resultado), 400
        
        except Exception as e:
            return jsonify({
                'exito': False,
                'mensaje': f'Error al procesar la solicitud: {str(e)}'
            }), 500


# Instancia global del controller
mano_controller = ManoController()
