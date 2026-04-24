from flask import request, jsonify
from services.entrenamiento_services import EntrenaciontoService

class EntrenaciontoController:
    """Controller para manejar entrenamiento del modelo de manos"""
    
    def __init__(self):
        self.entrenamiento_service = EntrenaciontoService()
    
    def entrenar_endpoint(self):
        """
        Endpoint para entrenar el modelo
        
        POST /api/manos/entrenar
        
        Parámetros:
            - ruta_dataset (opcional): Ruta a la carpeta de dataset (default: "data")
            
        Response:
            JSON con resultado del entrenamiento
        """
        try:
            # Obtener ruta del dataset (por defecto "data")
            ruta_dataset = request.form.get('ruta_dataset', 'data')
            
            print(f"\nIniciando entrenamiento con dataset en: {ruta_dataset}")
            
            # Entrenar modelo
            resultado = self.entrenamiento_service.entrenar_modelo(ruta_dataset)
            
            if resultado['exito']:
                return jsonify(resultado), 200
            else:
                return jsonify(resultado), 400
        
        except Exception as e:
            return jsonify({
                'exito': False,
                'mensaje': f'Error en el server: {str(e)}'
            }), 500


# Instancia global del controller
entrenamiento_controller = EntrenaciontoController()
