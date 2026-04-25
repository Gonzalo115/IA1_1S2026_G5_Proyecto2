"""
Extracción de features a partir de landmarks (sin cámara ni MediaPipe directo).

Contrato estable para ML: vector ``float32`` de longitud fija
``num_hand_slots * 63`` (por defecto 126 con dos huecos de mano).

Entrada típica: ``HandLandmarkerResult`` producido por ``hand_detection.HandDetector``.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np
from mediapipe.tasks.python.components.containers import landmark as landmark_module
from mediapipe.tasks.python.vision import hand_landmarker

NormalizedLandmark = landmark_module.NormalizedLandmark

FEATURE_SCHEMA_VERSION: int = 1

NUM_LANDMARKS: int = 21
COORDS_PER_LANDMARK: int = 3
FEATURES_PER_HAND: int = NUM_LANDMARKS * COORDS_PER_LANDMARK

WRIST_IDX: int = 0
MIDDLE_FINGER_MCP_IDX: int = 9


def feature_vector_length(*, num_hand_slots: int = 2) -> int:
    """Dimensión del vector de features para el número de huecos de mano dado."""
    return num_hand_slots * FEATURES_PER_HAND


def _landmarks_to_array(landmarks: Sequence[NormalizedLandmark]) -> np.ndarray:
    pts = np.empty((NUM_LANDMARKS, COORDS_PER_LANDMARK), dtype=np.float64)
    for i, lm in enumerate(landmarks):
        pts[i, 0] = 0.0 if lm.x is None else float(lm.x)
        pts[i, 1] = 0.0 if lm.y is None else float(lm.y)
        pts[i, 2] = 0.0 if lm.z is None else float(lm.z)
    return pts


def landmarks_to_feature_vector(
    landmarks: Sequence[NormalizedLandmark],
    *,
    eps: float = 1e-8,
) -> np.ndarray:
    """
    Una mano: coordenadas relativas a la muñeca, escala por distancia muñeca–MCP medio (XY).

    Returns:
        ``(63,)``, ``float32``.
    """
    n = len(landmarks)
    if n != NUM_LANDMARKS:
        raise ValueError(
            f"Se esperaban {NUM_LANDMARKS} landmarks por mano; se recibieron {n}."
        )
    pts = _landmarks_to_array(landmarks)
    wrist = pts[WRIST_IDX]
    centered = pts - wrist

    scale = float(np.linalg.norm(centered[MIDDLE_FINGER_MCP_IDX, :2]))
    if scale < eps:
        scale = float(np.max(np.linalg.norm(centered[:, :2], axis=1)) + eps)
        if scale < eps:
            scale = 1.0

    normalized = centered / scale
    return normalized.astype(np.float32).reshape(-1)


def multi_hand_landmarks_to_feature_vector(
    hands: Sequence[Sequence[NormalizedLandmark]],
    *,
    num_hand_slots: int = 2,
    eps: float = 1e-8,
) -> np.ndarray:
    """Varias manos en slots fijos; huecos vacíos en cero. Forma ``(num_hand_slots * 63,)``."""
    dim = num_hand_slots * FEATURES_PER_HAND
    out = np.zeros(dim, dtype=np.float32)
    for i, lm_list in enumerate(hands):
        if i >= num_hand_slots:
            break
        start = i * FEATURES_PER_HAND
        out[start : start + FEATURES_PER_HAND] = landmarks_to_feature_vector(
            lm_list, eps=eps
        )
    return out


def hand_landmarker_result_to_feature_vector(
    result: hand_landmarker.HandLandmarkerResult,
    *,
    num_hand_slots: int = 1,
    eps: float = 1e-8,
) -> np.ndarray:
    """
    Convierte la salida del landmarker en un vector fijo (ceros si no hay manos).

    Usar el mismo ``num_hand_slots`` en entrenamiento e inferencia.
    """
    if not result.hand_landmarks:
        return np.zeros(num_hand_slots * FEATURES_PER_HAND, dtype=np.float32)
    return multi_hand_landmarks_to_feature_vector(
        result.hand_landmarks,
        num_hand_slots=num_hand_slots,
        eps=eps,
    )
