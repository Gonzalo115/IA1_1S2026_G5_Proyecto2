import json
from pathlib import Path


class AdminService:
    def __init__(self):
        self.config_path = Path(__file__).resolve().parent.parent / "config" / "admin_config.json"

    def get_config(self):
        with open(self.config_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def update_config(self, data):
        config = self.get_config()

        allowed_fields = [
            "confidence_threshold",
            "telegram_enabled",
            "telegram_message_format",
            "available_signs"
        ]

        for field in allowed_fields:
            if field in data:
                config[field] = data[field]

        with open(self.config_path, "w", encoding="utf-8") as file:
            json.dump(config, file, indent=4, ensure_ascii=False)

        return config

    def get_available_signs(self):
        config = self.get_config()
        return config.get("available_signs", [])

    def get_history(self):
        config = self.get_config()
        return config.get("message_history", [])

    def add_history_item(self, item):
        config = self.get_config()

        if "message_history" not in config:
            config["message_history"] = []

        config["message_history"].append(item)

        with open(self.config_path, "w", encoding="utf-8") as file:
            json.dump(config, file, indent=4, ensure_ascii=False)

        return item