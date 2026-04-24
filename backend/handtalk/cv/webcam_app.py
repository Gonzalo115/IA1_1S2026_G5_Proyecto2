"""
Demostración: captura desde webcam con OpenCV, detección MediaPipe y dibujo de landmarks.

Ejecutar desde la carpeta `backend`:

    python -m handtalk.cv.webcam_app

Teclas: Q o ESC para salir.
"""

from __future__ import annotations

import time

import cv2

from handtalk.cv.hand_detector import HandDetector
from handtalk.cv.landmark_drawing import draw_hand_landmarks


def run(camera_index: int = 0, window_name: str = "HandTalk AI — Manos (Q/ESC salir)") -> None:
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"No se pudo abrir la cámara con índice {camera_index}.")

    detector = HandDetector()
    t0 = time.time()
    try:
        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                break

            timestamp_ms = int((time.time() - t0) * 1000)
            result = detector.process(frame, timestamp_ms)
            draw_hand_landmarks(frame, result)

            n = len(result.hand_landmarks)
            cv2.putText(
                frame,
                f"Manos: {n}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
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
        cap.release()
        cv2.destroyAllWindows()


def main() -> None:
    run()


if __name__ == "__main__":
    main()
