import os
from dotenv import load_dotenv
import psycopg2
from enum import Enum
from typing import List, Optional
from core.command_data import CommandData

load_dotenv()


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
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        database = os.getenv("DB_NAME", "knowledge")
        username = os.getenv("DB_USERNAME", "postgres")
        password = os.getenv("DB_PASSWORD", "postgres")

        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=username,
            password=password
        )
        cursor = conn.cursor()

        # Ищем план по ID или Name
        cursor.execute("""
            SELECT id, name FROM "Plan" WHERE id = %s OR name = %s
        """, (name_or_id, name_or_id))

        row = cursor.fetchone()
        if row is None:
            cursor.close()
            conn.close()
            return False

        plan_id = row[0]

        # Загружаем элементы плана
        cursor.execute("""
            SELECT commandName, commandPayload FROM "PlanItem" WHERE plan_id = %s ORDER BY number
        """, (plan_id,))

        rows = cursor.fetchall()
        self.commands.clear()
        for cmd_row in rows:
            self.commands.append(
                CommandData.createFromStructuredData(cmd_row[0], cmd_row[1])
            )

        cursor.close()
        conn.close()

        self.reset()
        return True

    def saveToDatabase(self, name: str) -> bool:
        """Сохраняет план и все элементы в БД в виде транзакции. Возвращает True при успехе."""
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        database = os.getenv("DB_NAME", "knowledge")
        username = os.getenv("DB_USERNAME", "postgres")
        password = os.getenv("DB_PASSWORD", "postgres")

        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=username,
            password=password
        )
        cursor = conn.cursor()

        try:
            # Вставляем или обновляем план
            cursor.execute("""
                INSERT INTO "Plan" (name) VALUES (%s)
                ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
                RETURNING id
            """, (name,))
            plan_id = cursor.fetchone()[0]

            # Удаляем старые элементы
            cursor.execute("""DELETE FROM "PlanItem" WHERE plan_id = %s""", (plan_id,))

            # Вставляем новые элементы
            for idx, cmd in enumerate(self.commands, start=1):
                cursor.execute("""
                    INSERT INTO "PlanItem" (number, plan_id, commandName, commandPayload)
                    VALUES (%s, %s, %s, %s)
                """, (idx, plan_id, cmd.commandName, cmd.commandPayload))

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Ошибка при сохранении плана: {e}")
            return False
        finally:
            cursor.close()
            conn.close()




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
