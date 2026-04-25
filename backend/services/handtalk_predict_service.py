"""Orquestación Flask: captura de frame y delegación en InferenceService."""

from __future__ import annotations

from typing import Any, Dict, Optional

from handtalk.cv.camera import WebcamCapture
from handtalk.inference_service import InferenceService

_inference: Optional[InferenceService] = None


def _get_inference() -> InferenceService:
    global _inference
    if _inference is None:
        _inference = InferenceService()
    return _inference


class HandTalkPredictService:
    """Una captura desde webcam + predicción (sin duplicar el bucle de test_model)."""

    def predict_from_webcam_once(self) -> Dict[str, Any]:
        with WebcamCapture(0) as cam:
            ok, frame = cam.read()
        if not ok or frame is None:
            return {"error": "No frame captured"}
        return _get_inference().predict_from_frame(frame)
