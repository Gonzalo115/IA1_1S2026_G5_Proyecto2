"""Suavizado de predicciones por ventana deslizante (moda sobre los últimos N valores)."""

from __future__ import annotations

from collections import Counter, deque
from typing import Deque, Generic, Hashable, TypeVar

T = TypeVar("T", bound=Hashable)


class ModeSmoothingWindow(Generic[T]):
    """
    Ventana deslizante de tamaño fijo; la salida es la etiqueta más frecuente.

    En empates, gana la etiqueta cuya **última aparición** en la ventana es más reciente
    (mejor continuidad en tiempo real).

    Coste por ``update``: O(N) con N pequeño (p. ej. 10), adecuado para bucles de vídeo.
    """

    __slots__ = ("_buf", "_window_size")

    def __init__(self, window_size: int = 10) -> None:
        if window_size < 1:
            raise ValueError("window_size debe ser >= 1.")
        self._window_size = window_size
        self._buf: Deque[T] = deque(maxlen=window_size)

    def clear(self) -> None:
        """Vacía la ventana."""
        self._buf.clear()

    def __len__(self) -> int:
        return len(self._buf)

    def update(self, prediction: T) -> T:
        """
        Añade una predicción y devuelve la moda suavizada sobre la ventana actual.

        La ventana puede estar incompleta al inicio; en ese caso se usa solo
        el histórico disponible (sigue siendo la moda de esos elementos).
        """
        self._buf.append(prediction)
        return self._mode_with_recency_tiebreak()

    def _mode_with_recency_tiebreak(self) -> T:
        counts = Counter(self._buf)
        best_count = max(counts.values())
        candidates = {k for k, v in counts.items() if v == best_count}
        if len(candidates) == 1:
            return next(iter(candidates))
        for label in reversed(self._buf):
            if label in candidates:
                return label
        return next(iter(candidates))
