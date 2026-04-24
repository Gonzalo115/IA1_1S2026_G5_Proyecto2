"""Dibujo de landmarks de mano sobre frames BGR (OpenCV)."""

from __future__ import annotations

import numpy as np
from mediapipe.tasks.python.vision import drawing_styles
from mediapipe.tasks.python.vision import drawing_utils
from mediapipe.tasks.python.vision import hand_landmarker

_HandLandmarksConnections = hand_landmarker.HandLandmarksConnections


def draw_hand_landmarks(
    frame_bgr: np.ndarray,
    detection: hand_landmarker.HandLandmarkerResult,
) -> None:
    """
    Dibuja conexiones y puntos de todas las manos detectadas sobre el frame (in-place).

    Args:
        frame_bgr: Imagen BGR uint8 (modificada en el mismo array).
        detection: Resultado de ``hand_detection.HandDetector.process``.
    """
    if not detection.hand_landmarks:
        return

    landmark_style = drawing_styles.get_default_hand_landmarks_style()
    connection_style = drawing_styles.get_default_hand_connections_style()

    for hand_landmarks in detection.hand_landmarks:
        drawing_utils.draw_landmarks(
            frame_bgr,
            hand_landmarks,
            _HandLandmarksConnections.HAND_CONNECTIONS,
            landmark_drawing_spec=landmark_style,
            connection_drawing_spec=connection_style,
        )
