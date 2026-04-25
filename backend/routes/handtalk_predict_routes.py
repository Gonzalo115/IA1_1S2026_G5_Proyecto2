from flask import Blueprint

from controllers.handtalk_predict_controller import handtalk_predict_controller

handtalk_predict_bp = Blueprint("handtalk_predict", __name__)


@handtalk_predict_bp.route("/predict", methods=["GET"])
def predict():
    """GET /predict — captura un frame y devuelve predicción cruda y suavizada."""
    return handtalk_predict_controller.predict_endpoint()
