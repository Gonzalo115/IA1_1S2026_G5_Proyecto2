from flask import Blueprint, jsonify, request
from services.admin_service import AdminService

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/api/admin")

admin_service = AdminService()


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
        "message": "Configuración actualizada correctamente",
        "config": updated_config
    }), 200


@admin_bp.route("/signs", methods=["GET"])
def get_signs():
    signs = admin_service.get_available_signs()
    return jsonify({
        "available_signs": signs
    }), 200


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
        "message": "Historial actualizado",
        "item": item
    }), 201