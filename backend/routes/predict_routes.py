from flask import Blueprint, current_app, jsonify

from services.predict_service import PredictService

predict_bp = Blueprint("predict", __name__)


def _predict_service() -> PredictService:
    return current_app.extensions["predict_service"]


@predict_bp.route("/predict", methods=["GET"])
def predict():
    result = _predict_service().predict_from_webcam_once()
    return jsonify(result)
