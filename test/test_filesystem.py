import sys
import os
import tempfile
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from context.context_root import ContextRoot
from core.command_processor import CommandProcessor
from core.command_result import CommandResult
from tools.init_tools import initTools


class TestFileSystemIntegration(unittest.TestCase):
    ctx_root = ContextRoot()
    cmd_processor = CommandProcessor(ctx_root)
    answers: list[CommandResult] = []
    should_continue = False

    def setUp(self):
        initTools(self.ctx_root)
        self.answers = []

    def callback(self, result: CommandResult):
        self.answers.append(result)

    def _process(self, text: str) -> CommandResult:
        """Вспомогательный метод для вызова process и получения результата."""
        self.answers = []
        self.cmd_processor.process(text, self.callback)
        return self.answers[-1] if self.answers else CommandResult()

    #---------------------------------------------------------------------#

    def test_save_to_file(self):
        """Команда 'Сохрани последний результат в файл' сохраняет данные в файл."""
        self.ctx_root.Context.lastResult = "Тестовый текст для сохранения"
        tmp_path = ""

        tmp_path = "test1.txt"

        try:
            self._process(f'/ Сохрани последний результат в файл : {{ "path": "{tmp_path}" }}')

            self.assertIsInstance(self.answers[0], CommandResult)
            self.assertIn("сохранены", self.answers[0].output_text)

            # Проверяем, что файл действительно создан и содержит данные
            self.assertTrue(os.path.exists(tmp_path))
            with open(tmp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertEqual(content, "Тестовый текст для сохранения")
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


if __name__ == "__main__":
    unittest.main()
