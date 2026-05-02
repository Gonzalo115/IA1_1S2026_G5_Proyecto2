"""Captura de vídeo desde webcam con OpenCV (sin MediaPipe ni lógica de manos)."""

from __future__ import annotations

from typing import Optional, Tuple

import cv2
import numpy as np


class WebcamCapture:
    """
    Abre un dispositivo de captura y expone lectura de frames BGR.

    Uso típico::

        with WebcamCapture(0) as cam:
            ok, frame = cam.read()
    """

    def __init__(self, camera_index: int = 0) -> None:
        self._camera_index = camera_index
        self._cap: Optional[cv2.VideoCapture] = None

    def open(self) -> None:
        if self._cap is not None:
            return
        self._cap = cv2.VideoCapture(self._camera_index)
        if not self._cap.isOpened():
            self._cap.release()
            self._cap = None
            raise RuntimeError(
                f"No se pudo abrir la cámara con índice {self._camera_index}."
            )

    def release(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    @property
    def is_opened(self) -> bool:
        return self._cap is not None and self._cap.isOpened()

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Lee el siguiente frame.

        Returns:
            (éxito, frame BGR uint8 o None si falla).
        """
        if self._cap is None:
            return False, None
        ok, frame = self._cap.read()
        if not ok or frame is None:
            return False, None
        return True, frame

    def __enter__(self) -> WebcamCapture:
        self.open()
        return self

    def __exit__(self, *args: object) -> None:
        self.release()
