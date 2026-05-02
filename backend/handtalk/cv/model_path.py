"""Resolución de la ruta al modelo Hand Landmarker de MediaPipe Tasks."""

from __future__ import annotations

import os
import urllib.request
from pathlib import Path

# Modelo oficial (MediaPipe Tasks). Si la URL cambia, actualizar aquí o usar
# la variable de entorno HANDTALK_HAND_LANDMARKER_MODEL.
_DEFAULT_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
)

_MODEL_FILENAME = "hand_landmarker.task"


def default_model_path() -> Path:
    """Ruta por defecto donde se guarda o se espera el archivo .task."""
    return Path(__file__).resolve().parent.parent / "models" / _MODEL_FILENAME


def resolve_hand_landmarker_model_path() -> str:
    """
    Devuelve una ruta absoluta al bundle .task.

    Orden de precedencia:
    1) Variable de entorno HANDTALK_HAND_LANDMARKER_MODEL
    2) Archivo en handtalk/models/hand_landmarker.task (descarga si no existe)
    """
    env = os.environ.get("HANDTALK_HAND_LANDMARKER_MODEL")
    if env:
        path = Path(env).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(
                f"HANDTALK_HAND_LANDMARKER_MODEL apunta a un archivo inexistente: {path}"
            )
        return str(path)

    path = default_model_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.is_file():
        _download_model(_DEFAULT_MODEL_URL, path)
    return str(path)


def _download_model(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".download")
    try:
        print(f"Descargando modelo Hand Landmarker a {dest} ...")
        urllib.request.urlretrieve(url, tmp)
        tmp.replace(dest)
    except Exception:
        if tmp.is_file():
            tmp.unlink(missing_ok=True)
        raise
