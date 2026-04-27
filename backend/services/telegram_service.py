import os
from datetime import datetime

import requests
from dotenv import load_dotenv

from services.admin_service import AdminService


load_dotenv()


class TelegramService:
    def __init__(self):
        self.admin_service = AdminService()
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

    def send_prediction_message(self, prediction, confidence=None):
        config = self.admin_service.get_config()

        if not config.get("telegram_enabled", False):
            return {
                "sent": False,
                "reason": "El envío a Telegram está desactivado desde administración"
            }

        message_format = config.get(
            "telegram_message_format",
            "Se detectó la seña: {prediction}"
        )

        message = message_format.format(
            prediction=prediction,
            confidence=confidence if confidence is not None else "N/A"
        )

        if not self.bot_token or not self.chat_id:
            return {
                "sent": False,
                "reason": "Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en el archivo .env",
                "message": message
            }

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        payload = {
            "chat_id": self.chat_id,
            "text": message
        }

        response = requests.post(url, json=payload, timeout=10)

        history_item = {
            "prediction": prediction,
            "confidence": confidence,
            "message": message,
            "sent": response.status_code == 200,
            "status_code": response.status_code,
            "created_at": datetime.now().isoformat()
        }

        self.admin_service.add_history_item(history_item)

        return history_item