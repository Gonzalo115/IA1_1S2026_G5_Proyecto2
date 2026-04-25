import time
import cv2
import joblib

from handtalk.cv import WebcamCapture, HandDetector
from handtalk.cv.features import hand_landmarker_result_to_feature_vector
from handtalk.smoother import ModeSmoothingWindow


MODEL_PATH = "models/modelo_manos.pkl"

model = joblib.load(MODEL_PATH)

start_time = time.time()
smoother = ModeSmoothingWindow(window_size=10)

try:
    with WebcamCapture(0) as cam:
        detector = HandDetector()

        while True:
            ok, frame = cam.read()
            if not ok:
                break

            timestamp_ms = int((time.time() - start_time) * 1000)
            result = detector.process(frame, timestamp_ms=timestamp_ms)

            features = hand_landmarker_result_to_feature_vector(
                result,
                num_hand_slots=1
            )

            if len(features) != 63:
                print("Error en features:", len(features))
                continue

            raw_prediction = model.predict([features])[0]

            # convertir numpy a tipo normal si aplica
            try:
                raw_prediction = raw_prediction.item()
            except:
                pass

            stable_prediction = smoother.update(raw_prediction)

            print(f"Raw: {raw_prediction} | Estable: {stable_prediction}")

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        detector.close()

finally:
    cv2.destroyAllWindows()