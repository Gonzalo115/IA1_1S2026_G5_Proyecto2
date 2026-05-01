import cv2
import mediapipe as mp
import joblib
import numpy as np
import os
from typing import Dict

class ManoService:
    """Servicio para detectar y clasificar señas de mano"""
    
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=True)
        self.modelo = None
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.modelo_path = os.path.join(base_dir, "models", "modelo_manos.pkl")
        self.cargar_modelo()
    
    def cargar_modelo(self) -> bool:
        try:
            if os.path.exists(self.modelo_path):
                paquete = joblib.load(self.modelo_path)

                if isinstance(paquete, dict) and "modelo" in paquete:
                    self.modelo = paquete["modelo"]
                    self.metadata = paquete.get("metadata", {})
                else:
                    self.modelo = paquete
                    self.metadata = {}

                print(f"Modelo cargado: {self.modelo_path}")
                return True
            else:
                print(f"Modelo no encontrado: {self.modelo_path}")
                return False

        except Exception as e:
            print(f"Error al cargar modelo: {str(e)}")
            return False

    def normalizar_landmarks(self, mano):
        base_x = mano.landmark[0].x
        base_y = mano.landmark[0].y
        base_z = mano.landmark[0].z

        puntos = []

        for p in mano.landmark:
            puntos.extend([
                p.x - base_x,
                p.y - base_y,
                p.z - base_z
            ])

        return puntos
    
    def analizar_imagen(self, imagen_array: np.ndarray) -> Dict:
        """
        Analiza una imagen y detecta la seña de mano
        
        Args:
            imagen_array: Array de numpy con la imagen
            
        Returns:
            Dict con predicción y confianza
        """
        try:
            print("Se está detectando seña de mano...")
            
            if self.modelo is None:
                return {
                    'exito': False,
                    'mensaje': 'El modelo no está cargado. Entrena el modelo primero.',
                    'prediccion': None,
                    'confianza': None
                }
            
            # Convertir a RGB si es necesario
            if len(imagen_array.shape) == 3 and imagen_array.shape[2] == 3:
                # Convertir BGR a RGB (OpenCV carga en BGR)
                imagen_rgb = cv2.cvtColor(imagen_array, cv2.COLOR_BGR2RGB)
            else:
                imagen_rgb = imagen_array
            
            # Procesar con MediaPipe
            resultado = self.hands.process(imagen_rgb)
            
            if not resultado.multi_hand_landmarks:
                return {
                    'exito': False,
                    'mensaje': 'No se detectó mano en la imagen',
                    'prediccion': None,
                    'confianza': None
                }
            
            # Procesar la mano detectada
            mano = resultado.multi_hand_landmarks[0]
            
            # Extraer puntos (21 landmarks * 3 = 63 valores)
            puntos = self.normalizar_landmarks(mano)
            
            # Hacer predicción
            prediccion = self.modelo.predict([puntos])[0]
            confianzas = self.modelo.predict_proba([puntos])[0]
            confianza_max = float(np.max(confianzas))
            
            # Obtener etiquetas del modelo
            etiquetas = self.modelo.classes_
            
            # Crear diccionario de confianzas por etiqueta
            confianzas_dict = {
                str(etiqueta): float(conf) 
                for etiqueta, conf in zip(etiquetas, confianzas)
            }
            
            print(f"Detección completada: {prediccion} (confianza: {confianza_max:.2%})")
            
            return {
                'exito': True,
                'prediccion': str(prediccion),
                'confianza': confianza_max,
                'confianzas_por_clase': confianzas_dict,
                'mensaje': f'Seña detectada: {prediccion}',
                'manos_detectadas': len(resultado.multi_hand_landmarks)
            }
        
        except Exception as e:
            print(f"Error al analizar imagen: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'exito': False,
                'mensaje': f'Error al analizar: {str(e)}',
                'prediccion': None,
                'confianza': None
            }
