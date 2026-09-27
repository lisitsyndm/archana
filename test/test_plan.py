import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from context.context_root import ContextRoot
from core.command_processor import CommandProcessor
from core.command_result import CommandResult
from tools.plan import RegisterPlanCommands


class TestPlanIntegration(unittest.TestCase):
    ctx_root = ContextRoot()
    cmd_processor = CommandProcessor(ctx_root)
    answers: list[CommandResult] = []
    should_continue = False

    def setUp(self):
        RegisterPlanCommands(self.ctx_root)
        self.answers = []

    def callback(self, result: CommandResult):
        self.answers.append(result)

    def _process(self, text: str) -> CommandResult:
        """Вспомогательный метод для вызова process и получения результата."""
        self.answers = []
        self.cmd_processor.process(text, self.callback)
        return self.answers[-1] if self.answers else CommandResult()

    #---------------------------------------------------------------------#

    def test_execute_plan(self):
        """Команда 'Выполни план' запускает выполнение плана."""
        result = self._process("/ Выполни план : ")

        self.assertIsInstance(self.answers[0], CommandResult)
        self.assertEqual(self.answers[0].output_text, "Выполнение плана начато")
        self.assertTrue(self.ctx_root.plan.planStatus.name == "Started")

    #---------------------------------------------------------------------#

    def test_reset_plan(self):
        """Команда 'Верни план в начало' сбрасывает план."""
        self._process("/ Верни план в начало : ")

        self.assertIsInstance(result, CommandResult)
        self.assertEqual(self.answers[0].output_text, "Готова начать план с начала")
        self.assertEqual(self.ctx_root.plan.step, 0)
        self.assertEqual(self.ctx_root.plan.planStatus.name, "Stopped")

    #---------------------------------------------------------------------#

    def test_continue_plan(self):
        """Команда 'Продолжи выполнение плана' продолжает выполнение."""
        self._process("/ Продолжи выполнение плана : ")

        self.assertIsInstance(self.answers[0], CommandResult)
        self.assertEqual(result.output_text, "План продолжен")
        self.assertEqual(self.ctx_root.plan.planStatus.name, "Started")

    #---------------------------------------------------------------------#

    def test_pause_plan(self):
        """Команда 'Останови выполнение плана' приостанавливает выполнение."""
        self._process("/ Останови выполнение плана : ")

        self.assertIsInstance(result, CommandResult)
        self.assertEqual(result.output_text, "Выполнение плана приостановлено")
        self.assertEqual(self.ctx_root.plan.planStatus.name, "Paused")

    #---------------------------------------------------------------------#

    def test_load_plan_from_db_not_exists(self):
        """Команда 'Загрузи план из базы данных' с несуществующим планом."""
        self._process('/ Загрузи план из базы данных : {"name": "nonExistentPlan"}')

        self.assertIsInstance(result, CommandResult)
        self.assertEqual(result.output_text, "План загружен")
        self.assertEqual(len(self.ctx_root.plan.commands), 0)

    #---------------------------------------------------------------------#

    def test_save_plan_to_db(self):
        """Команда 'Сохрани план в базу данных' сохраняет план."""
        self._process('/ Сохрани план в базу данных : {"name": "testPlan"}')

        self.assertIsInstance(result, CommandResult)
        self.assertEqual(result.output_text, "План сохранен")


if __name__ == "__main__":
    unittest.main()
