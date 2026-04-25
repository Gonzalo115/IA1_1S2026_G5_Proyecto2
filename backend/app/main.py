"""API FastAPI: estado, predicción por frame de webcam vía InferenceService."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException

from handtalk.cv.camera import WebcamCapture
from handtalk.inference_service import InferenceService

inference_service: Optional[InferenceService] = None
_webcam: Optional[WebcamCapture] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global inference_service, _webcam
    inference_service = InferenceService()
    _webcam = WebcamCapture(0)
    _webcam.open()
    yield
    if inference_service is not None:
        inference_service.close()
    if _webcam is not None:
        _webcam.release()


app = FastAPI(title="HandTalk AI", lifespan=lifespan)


@app.get("/")
def root() -> Dict[str, str]:
    return {"status": "API running"}


@app.get("/predict")
def predict() -> Dict[str, Any]:
    if inference_service is None or _webcam is None:
        raise HTTPException(status_code=503, detail="Servicio no inicializado.")
    ok, frame = _webcam.read()
    if not ok or frame is None:
        raise HTTPException(status_code=503, detail="No se pudo capturar un frame de la cámara.")
    return inference_service.predict_from_frame(frame)
