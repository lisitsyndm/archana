import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
from context.context_root import ContextRoot
from core.command_processor import CommandProcessor
from core.command_result import CommandResult
from tools.init_tools import initTools


class TestResearcherIntegration(unittest.TestCase):
    ctx_root = ContextRoot()
    cmd_processor = CommandProcessor(ctx_root)
    answers: list[CommandResult] = []
    should_continue = False

    def setUp(self):
        self.answers = []
        initTools(self.ctx_root)

    def callback(self, result: CommandResult):
        self.answers.append(result)

    def _process(self, text: str) -> CommandResult:
        """Вспомогательный метод для вызова process и получения результата."""
        self.answers = []
        self.cmd_processor.process(text, self.callback)
        return self.answers[-1] if self.answers else CommandResult()

    #---------------------------------------------------------------------#

    # @patch('tools.researcher.requests.post')
    def test_internet_search(self):
        """Команда 'Найти в интернете' возвращает результат поиска."""
        # Подменяем ответ API
        #mock_response = MagicMock()
        #mock_response.json.return_value = {"answer": "Перечисли три наиболее популярные реляционные базы данных. Верни только список."}
        #mock_post.return_value = mock_response

        result = self._process('/ Найти в интернете : {"text": "Перечисли три наиболее популярные реляционные базы данных. Верни только список."}')

        self.assertIsInstance(result, CommandResult)

        len_res = len(self.answers[0].output_text)
        res = len_res > 10

        print(f"Результат: {self.answers[0].output_text}")

        self.assertEqual(res, True)

        # Проверяем, что API был вызван с правильным запросом
        # mock_post.assert_called_once()
        # call_args = mock_post.call_args
        # self.assertEqual(call_args.kwargs['json']['messages'][0]['content'], "тестовый запрос")


if __name__ == "__main__":
    unittest.main()
