from flask import Flask, jsonify
from flask_cors import CORS

from handtalk.cv.camera import WebcamCapture
from handtalk.inference_service import InferenceService
from routes.rostro_routes import rostro_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(rostro_bp)

# Una sola instancia para toda la aplicación (no por petición).
inference_service = InferenceService()


@app.route("/", methods=["GET"])
def inicio():
    """Ruta de inicio - Verificar que el servidor está activo."""
    return jsonify(
        {
            "mensaje": "API de Detección de Rostros activa",
            "endpoints": {
                "detectar_rostro": "POST /api/rostros/detectar (enviar imagen)",
                "saludo": "GET /api/rostros/saludo",
                "predict_manos": "GET /predict (webcam + InferenceService)",
            },
        }
    )


@app.route("/predict", methods=["GET"])
def predict():
    """Captura un frame de la webcam y devuelve predicción cruda y suavizada."""
    with WebcamCapture(0) as cam:
        ok, frame = cam.read()
    if not ok or frame is None:
        return jsonify({"error": "No frame captured"})
    return jsonify(inference_service.predict_from_frame(frame))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
