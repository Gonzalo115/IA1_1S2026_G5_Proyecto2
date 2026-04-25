"""
Servicio de inferencia: compone detector, features, modelo sklearn y suavizado.

No modifica los módulos de visión; solo los orquesta.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, Optional, Union

import joblib
import numpy as np

from handtalk.cv.features import feature_vector_length, hand_landmarker_result_to_feature_vector
from handtalk.cv.hand_detection import HandDetector, HandDetectorConfig
from handtalk.smoother import ModeSmoothingWindow

# Una mano → 63 valores (coherente con feature_vector_length(num_hand_slots=1)).
_NUM_HAND_SLOTS = 1
_EXPECTED_FEATURE_DIM = feature_vector_length(num_hand_slots=_NUM_HAND_SLOTS)

# Ruta por defecto respecto a la carpeta ``backend`` del proyecto.
_DEFAULT_SKLEARN_MODEL = (
    Path(__file__).resolve().parent.parent / "models" / "modelo_manos.pkl"
)


class InferenceService:
    """
    Carga el modelo entrenado, el detector MediaPipe y el suavizado por moda.

    ``predict_from_frame`` espera un frame **BGR** (uint8) como devuelve OpenCV.
    """

    def __init__(
        self,
        model_path: Optional[Union[str, Path]] = None,
        *,
        smoother_window: int = 10,
        hand_detector_config: Optional[HandDetectorConfig] = None,
    ) -> None:
        path = Path(model_path) if model_path is not None else _DEFAULT_SKLEARN_MODEL
        if not path.is_file():
            raise FileNotFoundError(f"No se encontró el modelo: {path}")

        self._model = joblib.load(path)
        det_cfg = hand_detector_config or HandDetectorConfig(num_hands=_NUM_HAND_SLOTS)
        if det_cfg.num_hands != _NUM_HAND_SLOTS:
            raise ValueError(
                f"InferenceService usa {_NUM_HAND_SLOTS} mano(s) (63 features); "
                f"ajusta HandDetectorConfig.num_hands a {_NUM_HAND_SLOTS}."
            )

        self._detector = HandDetector(det_cfg)
        self._smoother = ModeSmoothingWindow(window_size=smoother_window)
        self._t0 = time.perf_counter()

    def _elapsed_ms(self) -> int:
        return int((time.perf_counter() - self._t0) * 1000)

    def predict_from_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Pipeline: MediaPipe → vector 63 → ``predict`` → suavizado.

        Returns:
            ``{"raw": ..., "stable": ...}`` o ``{"error": "No hand detected"}``.
        """
        detection = self._detector.process(frame, self._elapsed_ms())
        if not detection.hand_landmarks:
            return {"error": "No hand detected"}

        features = hand_landmarker_result_to_feature_vector(
            detection, num_hand_slots=_NUM_HAND_SLOTS
        )
        if features.shape[0] != _EXPECTED_FEATURE_DIM:
            raise RuntimeError(
                f"Dimensión de features inesperada: {features.shape[0]}; "
                f"se esperaban {_EXPECTED_FEATURE_DIM}."
            )

        raw_arr = self._model.predict(features.reshape(1, -1))
        raw_pred = raw_arr[0]
        if isinstance(raw_pred, np.generic):
            raw_pred = raw_pred.item()

        stable_pred = self._smoother.update(raw_pred)
        return {"raw": raw_pred, "stable": stable_pred}

    def close(self) -> None:
        """Libera el landmarker de MediaPipe."""
        self._detector.close()
