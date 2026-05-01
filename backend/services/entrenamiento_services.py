import os
import cv2
import mediapipe as mp
import joblib
import numpy as np

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from typing import Dict


class EntrenaciontoService:
    """Servicio para entrenar modelo de detección de señas de mano"""

    def __init__(self):
        self.modelo = None
        self.modelo_path = "./models/modelo_manos.pkl"
        self.hand_landmarker_path = "models/hand_landmarker.task"

        if not os.path.exists("./models"):
            os.makedirs("./models")

        if not os.path.exists(self.hand_landmarker_path):
            print(f"No se encontró el modelo de MediaPipe: {self.hand_landmarker_path}")

        base_options = python.BaseOptions(
            model_asset_path=self.hand_landmarker_path
        )

        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1
        )

        self.detector = vision.HandLandmarker.create_from_options(options)

    def normalizar_landmarks(self, mano):
        """
        Normaliza los landmarks tomando como referencia la muñeca.
        Esto ayuda a que el modelo aprenda la forma de la mano y no la posición exacta.
        """
        base_x = mano[0].x
        base_y = mano[0].y
        base_z = mano[0].z

        puntos = []

        for p in mano:
            puntos.extend([
                p.x - base_x,
                p.y - base_y,
                p.z - base_z
            ])

        return puntos

    def entrenar_modelo(self, ruta_dataset: str = "Data") -> Dict:
        try:
            print("Iniciando entrenamiento del modelo...")

            X = []
            y = []
            conteo_clases = {}
            extensiones_validas = (".jpg", ".jpeg", ".png")

            if not os.path.exists(ruta_dataset):
                return {
                    "exito": False,
                    "mensaje": f"La carpeta {ruta_dataset} no existe"
                }

            print(f"Leyendo imágenes de {ruta_dataset}...")

            etiquetas_encontradas = set()

            for etiqueta in sorted(os.listdir(ruta_dataset)):
                ruta_etiqueta = os.path.join(ruta_dataset, etiqueta)

                if not os.path.isdir(ruta_etiqueta):
                    continue

                etiquetas_encontradas.add(etiqueta)
                print(f"Procesando clasificación: {etiqueta}")

                for archivo in os.listdir(ruta_etiqueta):
                    if not archivo.lower().endswith(extensiones_validas):
                        continue

                    ruta_imagen = os.path.join(ruta_etiqueta, archivo)

                    try:
                        imagen = cv2.imread(ruta_imagen)

                        if imagen is None:
                            print(f"No se pudo leer la imagen: {ruta_imagen}")
                            continue

                        imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)

                        mp_image = mp.Image(
                            image_format=mp.ImageFormat.SRGB,
                            data=imagen_rgb
                        )

                        resultado = self.detector.detect(mp_image)

                        if resultado.hand_landmarks:
                            mano = resultado.hand_landmarks[0]

                            puntos = self.normalizar_landmarks(mano)

                            if len(puntos) != 63:
                                print(f"Landmarks inválidos en: {archivo}")
                                continue

                            X.append(puntos)
                            y.append(etiqueta)

                            conteo_clases[etiqueta] = conteo_clases.get(etiqueta, 0) + 1
                        else:
                            print(f"No se detectó mano en: {ruta_imagen}")

                    except Exception as e:
                        print(f"Error al procesar {archivo}: {str(e)}")
                        continue

            print(f"\nTotal de muestras extraídas: {len(X)}")
            print(f"Etiquetas encontradas: {sorted(etiquetas_encontradas)}")
            print(f"Cantidad por clase: {conteo_clases}")

            if len(X) == 0:
                return {
                    "exito": False,
                    "mensaje": "No hay datos para entrenar. Verifica que las imágenes tengan manos."
                }

            if len(set(y)) < 2:
                return {
                    "exito": False,
                    "mensaje": "Necesitas al menos 2 clasificaciones diferentes para entrenar."
                }

            usar_stratify = min(conteo_clases.values()) >= 2

            print("\nDividiendo datos en entrenamiento (70%) y prueba (30%)...")

            X_train, X_test, y_train, y_test = train_test_split(
                X,
                y,
                test_size=0.3,
                random_state=42,
                stratify=y if usar_stratify else None
            )

            print("Entrenando RandomForestClassifier...")

            self.modelo = RandomForestClassifier(
                n_estimators=300,
                max_depth=None,
                random_state=42,
                n_jobs=-1,
                class_weight="balanced"
            )

            self.modelo.fit(X_train, y_train)

            print("Evaluando modelo...")

            predicciones = self.modelo.predict(X_test)
            accuracy = accuracy_score(y_test, predicciones)

            reporte = classification_report(
                y_test,
                predicciones,
                output_dict=True,
                zero_division=0
            )

            metadata = {
                "etiquetas": sorted(list(set(y))),
                "total_muestras": len(X),
                "muestras_entrenamiento": len(X_train),
                "muestras_prueba": len(X_test),
                "conteo_clases": conteo_clases,
                "normalizacion": "landmarks normalizados usando la muñeca como punto base",
                "features": 63,
                "algoritmo": "RandomForestClassifier"
            }

            paquete_modelo = {
                "modelo": self.modelo,
                "metadata": metadata
            }

            joblib.dump(paquete_modelo, self.modelo_path)

            print(f"Modelo guardado en: {self.modelo_path}")
            print(f"Accuracy: {accuracy:.2%}")

            return {
                "exito": True,
                "mensaje": "Modelo entrenado exitosamente",
                "accuracy": float(accuracy),
                "total_muestras": len(X),
                "muestras_entrenamiento": len(X_train),
                "muestras_prueba": len(X_test),
                "etiquetas": sorted(list(set(y))),
                "conteo_clases": conteo_clases,
                "reporte": reporte
            }

        except Exception as e:
            print(f"Error en entrenamiento: {str(e)}")
            import traceback
            traceback.print_exc()

            return {
                "exito": False,
                "mensaje": f"Error en entrenamiento: {str(e)}"
            }

    def cargar_modelo(self) -> bool:
        try:
            if os.path.exists(self.modelo_path):
                paquete = joblib.load(self.modelo_path)

                if isinstance(paquete, dict) and "modelo" in paquete:
                    self.modelo = paquete["modelo"]
                    return True

                self.modelo = paquete
                return True

            return False

        except Exception as e:
            print(f"Error cargando modelo: {str(e)}")
            return False