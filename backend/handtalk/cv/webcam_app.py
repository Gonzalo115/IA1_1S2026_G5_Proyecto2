"""
Demostración: cámara → detección de manos → features (opcional en consola) → dibujo.

Ejecutar desde la carpeta ``backend``::

    python -m handtalk.cv.webcam_app

Teclas: Q o ESC para salir.
"""

from __future__ import annotations

import time

import cv2

from handtalk.cv.camera import WebcamCapture
from handtalk.cv.features import hand_landmarker_result_to_feature_vector
from handtalk.cv.hand_detection import HandDetector
from handtalk.cv.landmark_drawing import draw_hand_landmarks


def run(camera_index: int = 0, window_name: str = "HandTalk AI — Manos (Q/ESC salir)") -> None:
    with WebcamCapture(camera_index) as cam:
        detector = HandDetector()
        t0 = time.time()
        try:
            while True:
                ok, frame = cam.read()
                if not ok or frame is None:
                    break

                timestamp_ms = int((time.time() - t0) * 1000)
                detection = detector.process(frame, timestamp_ms)
                feature_vec = hand_landmarker_result_to_feature_vector(detection)

                draw_hand_landmarks(frame, detection)

                n = len(detection.hand_landmarks)
                cv2.putText(
                    frame,
                    f"Manos: {n} | feat: {feature_vec.shape[0]}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA,
                )
                cv2.imshow(window_name, frame)
                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), ord("Q"), 27):
                    break
        finally:
            detector.close()
        cv2.destroyAllWindows()


def main() -> None:
    run()


if __name__ == "__main__":
    main()
