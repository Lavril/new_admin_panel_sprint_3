import json
import os
from typing import Any, Dict


class JsonFileStorage:
    """Реализация хранилища, использующего локальный файл.

    Формат хранения: JSON
    """

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def save_state(self, state: Dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""
        with open(self.file_path, 'w') as f:
            json.dump(state, f, indent=4)

    def retrieve_state(self) -> Dict[str, Any]:
        """Получить состояние из хранилища."""
        if not os.path.exists(self.file_path):
            return {}

        with open(self.file_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}


class State:
    """Класс для работы с состояниями."""

    def __init__(self, storage: JsonFileStorage) -> None:
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа."""
        state_storage = self.storage.retrieve_state()
        state_storage[key] = value
        self.storage.save_state(state_storage)

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу."""
        return self.storage.retrieve_state().get(key)
