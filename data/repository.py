from abc import ABC, abstractmethod
from typing import List, Optional

from core.knowledge import Knowledge
from core.command_data import CommandData


class KnowledgeRepository(ABC):
    """ABC интерфейс для работы с таблицей knowledge."""

    @abstractmethod
    def search(self, query_embedding: list[float], limit: int = 1) -> Optional[str]:
        """Поиск по embedding. Возвращает text первой найденной записи или None."""
        ...

    @abstractmethod
    def upsert(self, name: str, text: str, embedding: list[float]) -> None:
        """Вставка или обновление записи."""
        ...


class PlanRepository(ABC):
    """ABC интерфейс для работы с таблицами Plan / PlanItem."""

    @abstractmethod
    def get_by_id_or_name(self, identifier: str) -> Optional[dict]:
        """
        Возвращает {'plan_id': int, 'items': List[tuple]} где items — список (commandName, commandPayload).
        Возвращает None, если план не найден.
        """
        ...

    @abstractmethod
    def save(self, name: str, commands: List[CommandData]) -> int:
        """
        Сохраняет план и элементы. Возвращает plan_id.
        """
        ...
