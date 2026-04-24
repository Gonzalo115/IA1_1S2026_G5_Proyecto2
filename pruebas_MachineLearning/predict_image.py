import cv2
import mediapipe as mp
import joblib

# Cargar modelo entrenado
modelo = joblib.load("model.pkl")

# Configurar MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True)

# Cargar imagen (CAMBIA ESTA RUTA)
ruta_imagen = "./pruebas/a.jpg"

imagen = cv2.imread(ruta_imagen)

if imagen is None:
    print("No se encontró la imagen")
    exit()

# Convertir a RGB
imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)

# Procesar con MediaPipe
resultado = hands.process(imagen_rgb)

if resultado.multi_hand_landmarks:
    for mano in resultado.multi_hand_landmarks:
        puntos = []

        for p in mano.landmark:
            puntos.extend([p.x, p.y, p.z])

        # Hacer predicción
        prediccion = modelo.predict([puntos])
        confianza = modelo.predict_proba([puntos])

        print("Predicción:", prediccion[0])
        print("Confianza:", max(confianza[0]))

else:
    print("No se detectó mano en la imagen")