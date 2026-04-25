import time
import cv2
import joblib

from handtalk.cv import WebcamCapture, HandDetector
from handtalk.cv.features import hand_landmarker_result_to_feature_vector
from handtalk.smoother import ModeSmoothingWindow


# =========================
# CONFIGURACIÓN
# =========================
MODEL_PATH = "models/modelo_manos.pkl"
WINDOW_SIZE = 10


# =========================
# INICIALIZACIÓN
# =========================
model = joblib.load(MODEL_PATH)
smoother = ModeSmoothingWindow(window_size=WINDOW_SIZE)
start_time = time.time()


# =========================
# EJECUCIÓN
# =========================
try:
    with WebcamCapture(0) as cam:
        detector = HandDetector()

        while True:
            ok, frame = cam.read()
            if not ok:
                print("⚠️ No se pudo capturar frame")
                break

            # Timestamp requerido por MediaPipe
            timestamp_ms = int((time.time() - start_time) * 1000)

            # Detección
            result = detector.process(frame, timestamp_ms=timestamp_ms)

            # Extracción de features (63)
            features = hand_landmarker_result_to_feature_vector(
                result,
                num_hand_slots=1
            )

            if len(features) != 63:
                print(f"⚠️ Features inválidos: {len(features)}")
                continue

            # Predicción
            raw_prediction = model.predict([features])[0]

            # Convertir numpy → tipo nativo
            try:
                raw_prediction = raw_prediction.item()
            except:
                pass

            # Confianza (si existe)
            try:
                proba = model.predict_proba([features])[0]
                confidence = max(proba)
            except:
                confidence = 0.0

            # Suavizado
            stable_prediction = smoother.update(raw_prediction)

            # Salida
            print(
                f"Raw: {raw_prediction} | "
                f"Estable: {stable_prediction} | "
                f"Confianza: {confidence:.2f}"
            )

            # Mostrar cámara (opcional pero útil para demo)
            cv2.imshow("HandTalk AI - Test", frame)

            # Salir con 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        detector.close()

finally:
    cv2.destroyAllWindows()