"""
Convierte landmarks de mano MediaPipe en un vector numérico fijo.

* Posición relativa a la muñeca (índice 0).
* Escala invariante: norma en el plano XY del vector muñeca → dedo medio MCP (índice 9).
* Salida float32, longitud fija: ``num_hand_slots * NUM_LANDMARKS * 3`` (por defecto 2 manos → 126).
"""

from __future__ import annotations

from typing import Sequence

import numpy as np
from mediapipe.tasks.python.components.containers import landmark as landmark_module
from mediapipe.tasks.python.vision import hand_landmarker

NormalizedLandmark = landmark_module.NormalizedLandmark

# Versión del esquema de features (incrementar si cambia la geometría u orden).
FEATURE_SCHEMA_VERSION: int = 1

NUM_LANDMARKS: int = 21
COORDS_PER_LANDMARK: int = 3
FEATURES_PER_HAND: int = NUM_LANDMARKS * COORDS_PER_LANDMARK  # 63

WRIST_IDX: int = 0
MIDDLE_FINGER_MCP_IDX: int = 9


def _landmarks_to_array(landmarks: Sequence[NormalizedLandmark]) -> np.ndarray:
    """Devuelve forma (21, 3) float64 con coordenadas x, y, z."""
    n = len(landmarks)
    if n != NUM_LANDMARKS:
        raise ValueError(
            f"Se esperaban {NUM_LANDMARKS} landmarks por mano; se recibieron {n}."
        )
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
    Una mano: resta muñeca, escala por distancia muñeca–MCP medio en XY, aplanado (63,).

    Args:
        landmarks: exactamente 21 ``NormalizedLandmark`` en orden MediaPipe.
        eps: evita división por cero si la escala es nula (se usa escala 1.0).

    Returns:
        ``np.ndarray`` de forma ``(63,)``, ``dtype=float32``.
    """
    pts = _landmarks_to_array(landmarks)
    wrist = pts[WRIST_IDX]
    centered = pts - wrist

    scale = float(np.linalg.norm(centered[MIDDLE_FINGER_MCP_IDX, :2]))
    if scale < eps:
        scale = float(
            np.max(np.linalg.norm(centered[:, :2], axis=1)) + eps
        )
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
    """
    Varias manos en slots fijos: rellena con ceros si hay menos de ``num_hand_slots``.

    Args:
        hands: lista de manos; cada elemento es una secuencia de 21 landmarks.
        num_hand_slots: número fijo de huecos (p. ej. 2 para ambas manos).

    Returns:
        Forma ``(num_hand_slots * 63,)``, ``dtype=float32``.
    """
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
    num_hand_slots: int = 2,
    eps: float = 1e-8,
) -> np.ndarray:
    """
    Convierte el resultado de ``HandLandmarker`` en un vector fijo.

    Si no hay manos detectadas, devuelve un vector de ceros de la longitud esperada.

    Args:
        result: salida de ``HandDetector.process`` / MediaPipe Tasks.
        num_hand_slots: huecos fijos para manos (orden: el que devuelve MediaPipe).

    Returns:
        ``np.ndarray`` de forma ``(num_hand_slots * 63,)``, ``dtype=float32``.
    """
    if not result.hand_landmarks:
        return np.zeros(num_hand_slots * FEATURES_PER_HAND, dtype=np.float32)
    return multi_hand_landmarks_to_feature_vector(
        result.hand_landmarks,
        num_hand_slots=num_hand_slots,
        eps=eps,
    )
