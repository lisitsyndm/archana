import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from core.context import Context
from core.context_root import ContextRoot
from core.command_processor import CommandProcessor
from core.command_result import CommandResult
from tools.context import RegisterContextCommands
from tools.init_tools import initTools
from core.knowledge import TextKnowledge



class TestContextIntegration(unittest.TestCase):
    ctx_root = ContextRoot()
    cmd_processor = CommandProcessor(ctx_root)
    answers : list[CommandResult] = []
    should_continue = False

    def setUp(self):
        #self.ctx_root = ContextRoot()
        #self.cmd_processor = CommandProcessor(self.ctx_root)
        initTools(self.cmd_processor)
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

    def test_context_show(self):
        """Команда 'Покажи весь контекст' возвращает имя текущего контекста."""
        self.answers = []
        self.ctx_root.Context.Name = "TestContext"

        self._process("/ Покажи весь контекст : ")

        self.assertIsInstance(self.answers[0], CommandResult)
        self.assertEqual(self.answers[0].output_text, "TestContext")

    #---------------------------------------------------------------------#

    def test_last_result(self):
        """Команда 'Покажи последний результат' возвращает последний результат."""
        self.ctx_root.Context.lastResult = "Тестовый результат"

        self._process("/ Покажи последний результат : ")

        self.assertIsInstance(self.answers[0], CommandResult)
        self.assertEqual(self.answers[0].output_text, "Последний результат :\n Тестовый результат")

    #---------------------------------------------------------------------#

    def test_variables_list_with_items(self):
        """Команда 'Покажи список переменных' возвращает список переменных."""

        self.ctx_root.Context.knowledge = [
            TextKnowledge("var1", "text1"),
            TextKnowledge("var2", "text2")
        ]

        self._process("/ Покажи список переменных : ")

        self.assertIsInstance(self.answers[0], CommandResult)
        self.assertIn("var1", self.answers[0].output_text)
        self.assertIn("var2", self.answers[0].output_text)

    #---------------------------------------------------------------------#

    def test_save_variable_new(self):
        """Команда 'Запомни последний результат как' сохраняет новый результат как новую переменную."""
        self.ctx_root.Context.lastResult = "Сохраняемый текст"
        self.ctx_root.Context.knowledge = []

        self._process("/ Запомни последний результат как : {\"name\": \"savedVar\"}")

        self.assertIsInstance(self.answers[0], CommandResult)
        self.assertIn("savedVar", self.answers[0].output_text)
        self.assertEqual(len(self.ctx_root.Context.knowledge), 1)
        self.assertEqual(self.ctx_root.Context.knowledge[0].text, "Сохраняемый текст")
        self.assertEqual(self.ctx_root.Context.knowledge[0].name, "savedVar")

    #---------------------------------------------------------------------#

    def test_show_variable_exists(self):
        """Команда 'Покажи переменную' возвращает значение существующей переменной."""

        self.ctx_root.Context.knowledge.append(TextKnowledge("myVar", "myValue"))

        self._process("/ Покажи переменную : {\"name\": \"myVar\"}")

        self.assertIsInstance( self.answers[0], CommandResult)
        self.assertIn("myValue", self.answers[0].output_text)

    #---------------------------------------------------------------------#

    def test_save_text_as_variable_new(self):
        """Команда 'Запомни текст как' сохраняет текст как новую переменную."""

        self._process('/ Запомни текст как : {"name": "testVar", "text": "testText"}')

        self.assertIsInstance(self.answers[0], CommandResult)
        self.assertIn("testVar", self.answers[0].output_text)
        self.assertEqual(self.ctx_root.Context.knowledge[0].text, "testText")
        self.assertEqual(self.ctx_root.Context.knowledge[0].name, "testVar")


if __name__ == "__main__":
    unittest.main()
