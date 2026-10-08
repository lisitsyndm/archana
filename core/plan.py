import logging
from enum import Enum
from typing import List, Optional
from core.command_data import CommandData
from data.pg_repository import PostgresPlanRepository

logger = logging.getLogger(__name__)


class PlanStatus(Enum):
    Stopped = 0
    Started = 1
    Paused = 2


class Plan:
    """Класс для управления планом выполнения команд."""

    planStatus: PlanStatus = PlanStatus.Stopped
    step: int = 0
    commands: List[CommandData]

    def __init__(self):
        """Инициализация пустого плана."""
        self.planStatus = PlanStatus.Stopped
        self.step = 0
        self.commands: List[CommandData] = []

    def next(self) -> Optional[CommandData]:
        """Возвращает следующую команду и продвигает шаг. Возвращает None, если команда нет."""
        if not self.commands:
            return None

        res: Optional[CommandData] = None

        if self.step < len(self.commands):
            res = self.commands[self.step]
            self.step += 1
        else:
            self.planStatus = PlanStatus.Stopped

        return res

    def restart(self):
        """Перезапускает план: сбрасывает шаг на 0 и устанавливает статус Started."""
        self.step = 0
        self.planStatus = PlanStatus.Started

    def reset(self):
        """Полный сброс: шаг=0, статус=Stopped, очищает массив commands."""
        self.step = 0
        self.planStatus = PlanStatus.Stopped
        self.commands.clear()

    def proceed(self):
        """Устанавливает статус Started."""
        self.planStatus = PlanStatus.Started

    def pause(self):
        """Устанавливает статус Paused."""
        self.planStatus = PlanStatus.Paused

    def loadFromDatabase(self, name_or_id: str) -> bool:
        """Загружает план из БД по названию или ID. Возвращает True при успехе."""
        repo = PostgresPlanRepository()
        result = repo.get_by_id_or_name(name_or_id)

        if result is None:
            return False

        items = result["items"]
        self.commands.clear()
        for cmd_name, cmd_payload in items:
            self.commands.append(
                CommandData.createFromStructuredData(cmd_name, cmd_payload)
            )

        self.reset()
        return True

    def saveToDatabase(self, name: str) -> bool:
        """Сохраняет план и все элементы в БД в виде транзакции. Возвращает True при успехе."""
        try:
            repo = PostgresPlanRepository()
            repo.save(name, self.commands)
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении плана: {e}")
            return False


def fillTestPlan(plan: Plan):
    plan.commands.append(
        CommandData.createFromStructuredData(
            "Запомни текст как",
            '{"name":"Преимущества Redis", "text":"Преимущество 3, Преимущество 4, преимущество 5"}'
        )
    )
    plan.commands.append(
        CommandData.createFromStructuredData(
            "Запомни текст как",
            '{"name":"Преимущества Postgres", "text":"Преимущество 1, Преимущество 2, преимущество 3, Преимущество 4"}'
        )
    )
    plan.commands.append(
        CommandData.createFromStructuredData(
            "Покажи переменную",
            '{"name":"Преимущества Postgres"}'
        )
    )
