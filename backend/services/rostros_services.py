import cv2
import numpy as np
from typing import Dict, List, Tuple

class RostrosService:
    """Servicio para detectar rostros en imágenes"""
    
    def __init__(self):
        # Haar Cascades - Ya aprendio que es un rostro, ahora vamos a enseñarle a la computadora a reconocerlo
        # haarcascade_frontalface_default.xml -> Es un archivo que contiene los datos necesarios para detectar rostros
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def detectar_rostros(self, imagen_array: np.ndarray) -> Dict:
        """
        Detecta rostros en una imagen
        
        Args:
            imagen_array: Array de numpy con la imagen
            
        Returns:
            Dict con información de rostros detectados
        """
        try:
            print("Se está detectando rostro...")
            
            # gris -> Imagen en escala de grises
            gray = cv2.cvtColor(imagen_array, cv2.COLOR_BGR2GRAY)
            
            # faces -> Lista de coordenadas de los rostros detectados en la imagen
            # MultiScale -> Es un algoritmo para detectar objetos a diferentes escalas
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            # Preparar información de rostros detectados
            rostros_detectados = []
            for (x, y, w, h) in faces:
                rostros_detectados.append({
                    'x': int(x),
                    'y': int(y),
                    'ancho': int(w),
                    'alto': int(h)
                })
            
            cantidad = len(rostros_detectados)
            print(f"Detección completada: {cantidad} rostro(s) encontrado(s)")
            
            return {
                'exito': True,
                'cantidad_rostros': cantidad,
                'rostros': rostros_detectados,
                'mensaje': f'Se detectaron {cantidad} rostro(s)'
            }
            
        except Exception as e:
            print(f"Error al detectar rostros: {str(e)}")
            return {
                'exito': False,
                'cantidad_rostros': 0,
                'rostros': [],
                'mensaje': f'Error en detección: {str(e)}'
            }
