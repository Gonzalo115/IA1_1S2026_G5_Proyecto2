from flask import jsonify

from services.handtalk_predict_service import HandTalkPredictService


class HandTalkPredictController:
    def __init__(self) -> None:
        self._service = HandTalkPredictService()

    def predict_endpoint(self):
        result = self._service.predict_from_webcam_once()
        return jsonify(result), 200


handtalk_predict_controller = HandTalkPredictController()
