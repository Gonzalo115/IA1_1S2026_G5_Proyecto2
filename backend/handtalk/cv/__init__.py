"""
Visión por computador HandTalk: cámara, detección de manos, features y dibujo opcional.

Integración ML típica::

    from handtalk.cv import WebcamCapture, HandDetector
    from handtalk.cv.features import hand_landmarker_result_to_feature_vector

    with WebcamCapture(0) as cam:
        det = HandDetector()
        ok, frame = cam.read()
        out = det.process(frame, timestamp_ms=0)
        x = hand_landmarker_result_to_feature_vector(out, num_hand_slots=1)  # (63,) float32
        det.close()
"""

from handtalk.cv.camera import WebcamCapture
from handtalk.cv.hand_detection import HandDetector, HandDetectorConfig

__all__ = [
    "WebcamCapture",
    "HandDetector",
    "HandDetectorConfig",
]
