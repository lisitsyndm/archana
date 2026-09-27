import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from context.context_root import ContextRoot
from core.command_processor import CommandProcessor
from core.command_result import CommandResult
from tools.database import RegisterDatabaseCommands
from tools.init_tools import initTools


class TestDatabaseIntegration(unittest.TestCase):
    ctx_root = ContextRoot()
    cmd_processor = CommandProcessor(ctx_root)
    answers : list[CommandResult] = []
    should_continue = False

    def setUp(self):
        #self.ctx_root = ContextRoot()
        #self.cmd_processor = CommandProcessor(self.ctx_root)
        initTools(self.ctx_root)
        #self.answers[CommandResult] = []
        #self.should_continue = False

    def callback(self, result: CommandResult):
            self.answers.append (result)

    def _process(self, text: str) -> CommandResult:
        """Вспомогательный метод для вызова process и получения результата."""
        self.answers = []
        self.cmd_processor.process(text, self.callback)
        # Возвращаем последний результат (первые результаты могут быть от плана)

    #---------------------------------------------------------------------#

    def test_load_from_database_existing(self):
        """Команда 'Найди в БД' находит существующий ключ."""
        # Сначала сохраняем
        self._process('/ Сохрани в БД : {"name": "searchKey", "text": "searchValue"}')
        # Потом ищем
        self._process('/ Найди в БД : {"query": "searchKey"}')

        self.assertIsInstance(self.answers[0], CommandResult)
        self.assertEqual(self.answers[0].output_text, "searchValue")

if __name__ == "__main__":
    unittest.main()
