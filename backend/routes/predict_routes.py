from flask import Blueprint, current_app, jsonify

from services.predict_service import PredictService
from services.telegram_service import TelegramService

predict_bp = Blueprint("predict", __name__)

telegram_service = TelegramService()


def _predict_service() -> PredictService:
    return current_app.extensions["predict_service"]


@predict_bp.route("/predict", methods=["GET"])
def predict():
    result = _predict_service().predict_from_webcam_once()

    if "error" in result:
        return jsonify(result), 200

    prediction = result.get("stable") or result.get("raw")
    confidence = result.get("confidence")

    if prediction:
        telegram_result = telegram_service.send_prediction_message(
            prediction=prediction,
            confidence=confidence
        )

        result["telegram"] = telegram_result

    return jsonify(result), 200