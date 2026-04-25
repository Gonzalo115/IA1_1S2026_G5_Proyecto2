"""Captura de frame y delegación en InferenceService (sin lógica de visión interna)."""

from __future__ import annotations

from typing import Any, Dict

from handtalk.cv.camera import WebcamCapture
from handtalk.inference_service import InferenceService


class PredictService:
    def __init__(self, inference: InferenceService) -> None:
        self._inference = inference

    def predict_from_webcam_once(self) -> Dict[str, Any]:
        with WebcamCapture(0) as cam:
            ok, frame = cam.read()
        if not ok or frame is None:
            return {"error": "No frame captured"}
        return self._inference.predict_from_frame(frame)
