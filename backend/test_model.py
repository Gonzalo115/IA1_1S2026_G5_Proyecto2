import time
import joblib
from collections import Counter

from handtalk.cv import WebcamCapture, HandDetector
from handtalk.cv.features import hand_landmarker_result_to_feature_vector

# =========================

# CONFIGURACIÓN

# =========================

MODEL_PATH = "models/modelo_manos.pkl"
HISTORY_SIZE = 10  # tamaño de ventana para suavizado

# =========================

# CARGAR MODELO

# =========================

model = joblib.load(MODEL_PATH)

# =========================

# INICIALIZAR

# =========================

start_time = time.time()
history = []

# =========================

# LOOP PRINCIPAL

# =========================

with WebcamCapture(0) as cam:
detector = HandDetector()

```
while True:
    ok, frame = cam.read()
    if not ok:
        break

    # Timestamp correcto (monotónico)
    timestamp_ms = int((time.time() - start_time) * 1000)

    # Detección
    result = detector.process(frame, timestamp_ms=timestamp_ms)

    # Features (63 valores, 1 mano)
    features = hand_landmarker_result_to_feature_vector(
        result,
        num_hand_slots=1
    )

    # Validación de longitud
    if len(features) != 63:
        print("⚠️ Error: tamaño de features incorrecto:", len(features))
        continue

    # Predicción
    prediction = model.predict([features])[0]

    # Probabilidades (confianza)
    try:
        proba = model.predict_proba([features])[0]
        confidence = max(proba)
    except:
        confidence = 0.0

    # =========================
    # SUAVIZADO
    # =========================
    history.append(prediction)

    if len(history) > HISTORY_SIZE:
        history.pop(0)

    final_prediction = Counter(history).most_common(1)[0][0]

    # =========================
    # SALIDA
    # =========================
    print(
        f"Predicción: {prediction} | "
        f"Estable: {final_prediction} | "
        f"Confianza: {confidence:.2f}"
    )

    # Salir con tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

detector.close()
```
