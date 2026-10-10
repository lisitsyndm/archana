import os
import logging
import time
import json
from typing import Callable

from dotenv import load_dotenv

from typing import List
from core.command import Command
from llm.llm_client import LLMClient
from core.command_result import CommandResult
from core.helpers import fillKnowledge
from core.plan import PlanStatus
from core.command_data import *
from core.exceptions import *
from core.logger import *
from observability.metrics import *

load_dotenv()

logger = logging.getLogger(__name__)


class CommandProcessor:
    ctx_root = None

    def __init__(self, ctx_root):
        self.ctx_root = ctx_root
        self.Commands: List[Command] = []

    #-----------------------------------------------------------------------------#

    def process(self, text: str, callback: Callable[[CommandResult], None]):

        result = self.process_command(text)

        callback(result)

        while( self.ctx_root.plan.planStatus == PlanStatus.Started ):
            commandData: CommandData = self.ctx_root.plan.next()
            if commandData is None: break
            result = self.process_command( f"/ {commandData.commandName} : {commandData.commandPayload}"  )
            callback(result)

    #-----------------------------------------------------------------------------#

    def process_command(self, text: str) -> CommandResult:
        """ Выполняет текстовую команду
        Команда может быть в формате: / <название команды> : <параметры в формате JSON>
        либо в виде простого текста.
        А текст можно вставдять переменные из контекста <@ название переменной @>"""

        start_time = time.time()
        command: Command = None
        payload: str = ""
        data: dict = {}
        command_type = ""

        logger.info(f"====================================================================")
        logger.info(f"Обработка сообщения: '{text}'")

        try:
            if text.startswith("/"):
                logger.info("Сообщение классифицировано как скилл.")
                command_type = "direct"
                command, payload, data = self._convert_skill_to_command(text)
                if command is None:
                    return CommandResult(f"Не найден скилл: {command_name}")

            else:
                logger.info("Сообщение классифицировано как произвольный текст.")
                command_type = "llm-classified"
                command, payload, data = self._convert_text_to_command(text)

                if command is None:
                    logger.info("Сообщение не распознано как вызов инструмента с помощью произвольного текста.")
                    command, payload, data = self._convert_text_to_llm_command(text)

            logger.info(f"Вызов команды: {command.Name}")
            logger.info(f"Параметры: {data}")

            result = command.exec(self.ctx_root, data)
            self.ctx_root.histories.append(CommandData.createFromStructuredData(command.Name, payload))
            if (result.update_result):
                self.ctx_root.Context.lastResult = result.output_text

            process_command_total.labels(status="success", type=command_type).inc()
            duration = time.time() - start_time
            process_command_duration_seconds.observe(duration)

            return result

        except Exception as e:
            logger.error(f"Ошибка при выполнении команды: {e}")
            process_command_total.labels(status="error", type=command_type).inc()
            duration = time.time() - start_time
            process_command_duration_seconds.observe(duration)

            return CommandResult(f"Ошибка при выполнении команды: {e}")


    #-----------------------------------------------------------------------------#

    def _find_command(self, name: str) -> Command:
        command_name = " ".join(name.lower().split())
        command: Command = None
        for cmd in self.Commands:
            if cmd.TechName == command_name:
                command = cmd
                logger.info(f"Команда найдена: {command.Name}")
                break
        return command

    #-----------------------------------------------------------------------------#

    def _classify(self, text: str) -> str:
        cmds = ", ".join(cmd.Name for cmd in self.Commands)
        prompt = f"""Определи к какой команде из списка: {cmds} относится следующий текст: {text}.
            Ответ должен быть только названием команды.
            Верни только название команды из списка.
            Ответ долженв точности совпадать с названием команды из списка.
            Если команду найти нельзя, верни 'Нет'."""

        return LLMClient.get_instance().invoke(prompt, metric_name="llm_classification")

    #-----------------------------------------------------------------------------#

    def _convert_text_to_command (self, text: str) -> str:

        logger.info(f"_convert_text_to_command:")

        """Подготавливает вызов инструмента LLM на основе текста от пользователя.
        Сначала на основе введенного текста, определяем инструмент.
        Потом подготавливаем параметры его вызова также с помощью LLM.
        Возвращает кортеж из:
            - command - инструмент вызова LLM,
            - payload - json в виде строки с параметрами вызова (переменные еще не подставлены в текст)
            - data - словарь с параметрами вызова (переменные уже подставлены в текст)
        """
        command: Command = None
        payload: str = ""
        data: dict = {}

        logger.info(f"Ищем команду с помощью LLM.")
        logger.info(f"По тексту: {text}")
        command_name = self._classify(text)

        logger.info(f"Команда классифицирована как: {command_name}")
        command = self._find_command(command_name)

        if command is not None and command.data_class is not None and text != "":
            logger.info(f"Найден tool: {command.Name}")
            payload = self._parse_command_data_using_llm (command, text)
            logger.info(f"Параметры: {payload}")
            data = self._parse_data(self._fill_variables(payload))
            logger.info(f"Структурированные параметры: {data}")
        else: ("Не выполнено условие: command is not None and command.data_class is not None and text != ''")

        logger.info(f"Возврат")
        return command, payload, data

    #-----------------------------------------------------------------------------#

    def _convert_text_to_llm_command (self, text: str) -> str:
        """Подготавливает вызов инструмента LLM.
        Применяется только после того как текст пользователя не был распознан как другая команда.
        Поскольку мы заведомо имеем дело с текстом на естественном языке,
        преобразуем его в параметры вызова инструмента упрощенным образом.
        Возвращает кортеж из:
            - command - инструмент вызова LLM,
            - payload - json в виде строки с параметрами вызова (переменные еще не подставлены в текст)
            - data - словарь с параметрами вызова (переменные уже подставлены в текст)
        """

        command: Command = None
        payload: str = ""
        data: dict = {}

        logger.info(f"_convert_text_to_llm_command")
        logger.info(f"Переданный текст: {text}")

        command = self._find_command("Вызов LLM")

        if command is None:
            raise LLMSkillNotFound()

        text = text.replace('"', '\\"')
        payload = '{"text" : "' + text + '"}'
        data = self._parse_data(self._fill_variables(payload))

        logger.info(f"Выход из _convert_text_to_llm_command")

        return command, payload, data

    #-----------------------------------------------------------------------------#

    def _fill_variables(self, command_text: str) -> str:
        logger.info(f"_fill_variables:")
        logger.info(f"Подставляем переменные в текст команды: {command_text}")
        text = command_text.strip()
        text = fillKnowledge(self.ctx_root, text)
        text = text.replace("<!@", "<@").replace("@!>", "@>")

        return text

    #-----------------------------------------------------------------------------#

    def _convert_skill_to_command (self, text: str) -> tuple[Command, str, dict]:

        logger.info(f"_convert_skill_to_command:")

        """Подготавливает вызов инструмента LLM.
        Применяется только после того как текст распознан как скилл.
        Т.е. имеет структуру: / <название команды> : <параметры в формате JSON>
        Также корректно обрабатывает ситуации:
            - / <название команды>
            - / <название команды> : <просто текст>
              В этом случае весь текст сохраняется в единственное поле "text".
        Возвращает кортеж из:
            - command - инструмент вызова LLM,
            - payload - json в виде строки с параметрами вызова (переменные еще не подставлены в текст)
            - data - словарь с параметрами вызова (переменные уже подставлены в текст)
        """
        command = None
        payload = ""
        data = {}

        parts = text.split(":", 1)
        command_name = parts[0].strip()
        command_name = command_name.replace("/", "")

        payload = parts[1] if len(parts) > 1 else ""

        command = self._find_command(command_name)
        data = self._parse_data(self._fill_variables(payload))

        return command, payload, data

    #-----------------------------------------------------------------------------#

    def _parse_data(self, payload: str):

        logger.info(f"_parse_data")
        logger.info(f"Парсим JSON: {payload}")

        data = {}

        try:
            payload = str(payload).replace("\n", "\\n").replace("\r", "\\r")
            data = json.loads(payload)

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            data = {"text": str(payload)}

        return data

    #-----------------------------------------------------------------------------#

    def getKnowledgeTextByName(self, aname: str):
        for k in self.ctx_root.Context.knowledge:
            if k.name == aname:
                return k.asText()
        return None

    #-----------------------------------------------------------------------------#

    def _parse_command_data_using_llm (self, cmd: Command, user_input: str) -> str:

        logger.info(f"_parse_command_data_using_llm")
        logger.info(f"Определяем параметры команды {cmd.Name} с помощью LLM.")

        parser = JsonOutputParser(pydantic_object = cmd.data_class)
        prompt = PromptTemplate (
            input_variables=["fields", "user_input", "format_instructions"],
            template = """Найди в сообщении пользователя следующие значения: {fields}
                Если в сообщении пользователя нет необходимых данных, не придумывай ничего, оставляй поля пустыми!
                Если среди полей есть даты, и в них не задан день, месяц или год, считай, что даты не заданы.
                Сообщение: {user_input}
                Инструкции форматирования: {format_instructions}
                Верни ТОЛЬКО JSON!
                """)

        fields = ""

        for name, field_info in cmd.data_class.model_fields.items():
            if fields != "":
                fields += f", "
            fields += f"{field_info.description} ({name})"

        return LLMClient.get_instance().invoke_with_parser(
            prompt_template=prompt,
            parser=parser,
            fields=fields,
            user_input=user_input,
            metric_name="llm_data_prep",
        )
