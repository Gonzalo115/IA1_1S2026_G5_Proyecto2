from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

from handtalk.inference_service import InferenceService
from routes.predict_routes import predict_bp
from routes.rostro_routes import rostro_bp
from services.predict_service import PredictService
from routes.admin_routes import admin_bp
from routes.entrenar_routes import entrenar_bp
from routes.senas_routes import senas_bp

app = Flask(__name__)
CORS(app)

# Instancia única compartida por toda la app (inyectada al servicio de predicción).
inference_service = InferenceService()
app.extensions["predict_service"] = PredictService(inference_service)

app.register_blueprint(rostro_bp)
app.register_blueprint(predict_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(entrenar_bp)
app.register_blueprint(senas_bp)

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
                "entrenar": "POST /entrenar",
            },
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8000)
