"""Detección de manos con MediaPipe Tasks (solo inferencia de landmarks)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np
import mediapipe as mp

from mediapipe.tasks.python.core import base_options as base_options_module
from mediapipe.tasks.python.vision import hand_landmarker
from mediapipe.tasks.python.vision.core import vision_task_running_mode

from handtalk.cv.model_path import resolve_hand_landmarker_model_path

_BaseOptions = base_options_module.BaseOptions
_HandLandmarker = hand_landmarker.HandLandmarker
_HandLandmarkerOptions = hand_landmarker.HandLandmarkerOptions
_Image = mp.Image
_ImageFormat = mp.ImageFormat
_RunningMode = vision_task_running_mode.VisionTaskRunningMode


@dataclass
class HandDetectorConfig:
    """Parámetros del landmarker."""

    num_hands: int = 2
    min_hand_detection_confidence: float = 0.5
    min_hand_presence_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
    model_path: Optional[str] = None


class HandDetector:
    """
    HandLandmarker en modo VIDEO (frames consecutivos).

    Entrada: imagen BGR (OpenCV). Salida: HandLandmarkerResult.
    """

    def __init__(self, config: Optional[HandDetectorConfig] = None) -> None:
        self._config = config or HandDetectorConfig()
        model_path = self._config.model_path or resolve_hand_landmarker_model_path()

        with open(model_path, "rb") as f:
            model_buffer = f.read()

        options = _HandLandmarkerOptions(
            base_options=_BaseOptions(model_asset_buffer=model_buffer),
            running_mode=_RunningMode.VIDEO,
            num_hands=self._config.num_hands,
            min_hand_detection_confidence=self._config.min_hand_detection_confidence,
            min_hand_presence_confidence=self._config.min_hand_presence_confidence,
            min_tracking_confidence=self._config.min_tracking_confidence,
        )

        self._landmarker = _HandLandmarker.create_from_options(options)

    def process(
        self, frame_bgr: np.ndarray, timestamp_ms: int
    ) -> hand_landmarker.HandLandmarkerResult:
        if frame_bgr.ndim != 3 or frame_bgr.shape[2] != 3:
            raise ValueError("Se espera una imagen BGR con 3 canales (H, W, 3).")

        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

        mp_image = _Image(
            image_format=_ImageFormat.SRGB,
            data=rgb
        )

        return self._landmarker.detect_for_video(mp_image, timestamp_ms)

    def close(self) -> None:
        self._landmarker.close()