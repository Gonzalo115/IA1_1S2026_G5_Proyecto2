from flask import Blueprint, jsonify, request
import os
import joblib
from services.admin_service import AdminService
from services.telegram_service import TelegramService

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/api/admin")
admin_service = AdminService()
telegram_service = TelegramService()


@admin_bp.route("/config", methods=["GET"])
def get_config():
    config = admin_service.get_config()
    return jsonify(config), 200


@admin_bp.route("/config", methods=["PUT"])
def update_config():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No se enviaron datos"}), 400

    updated_config = admin_service.update_config(data)

    return jsonify({
        "message": "Configuración administrativa actualizada correctamente",
        "config": updated_config
    }), 200


@admin_bp.route("/modelo/clases", methods=["GET"])
def get_modelo_clases():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    modelo_path = os.path.join(base_dir, "models", "modelo_manos.pkl")
    if not os.path.isfile(modelo_path):
        return jsonify({"clases": [], "entrenado": False}), 200
    try:
        paquete = joblib.load(modelo_path)
        if isinstance(paquete, dict):
            clases = paquete.get("metadata", {}).get("etiquetas", [])
        else:
            clases = list(paquete.classes_)
        return jsonify({"clases": sorted(clases), "entrenado": True}), 200
    except Exception as e:
        return jsonify({"clases": [], "entrenado": False, "error": str(e)}), 200


@admin_bp.route("/history", methods=["GET"])
def get_history():
    history = admin_service.get_history()

    return jsonify({
        "message_history": history
    }), 200


@admin_bp.route("/history", methods=["POST"])
def add_history():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No se enviaron datos"}), 400

    item = admin_service.add_history_item(data)

    return jsonify({
        "message": "Mensaje agregado al historial correctamente",
        "item": item
    }), 201

@admin_bp.route("/telegram/test", methods=["POST"])
def test_telegram():
    data = request.get_json() or {}

    prediction = data.get("prediction", "Prueba desde HandTalk")
    confidence = data.get("confidence", None)

    result = telegram_service.send_prediction_message(
        prediction=prediction,
        confidence=confidence
    )

    return jsonify(result), 200