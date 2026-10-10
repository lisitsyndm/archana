from core.command import Command
from core.command_result import CommandResult
from core.context import Context
from core.context_root import ContextRoot
from core.command_processor import CommandProcessor
from pydantic import BaseModel, Field
from core.knowledge import Knowledge, TextKnowledge
from core.helpers import fillKnowledge
from core.logger import *

logger = logging.getLogger(__name__)

#-----------------------------------------------------------------------------------------------------#
# deprecated

class ContextShowCommand(Command):
    def __init__(self):
        super().__init__(name="Покажи весь контекст")

    def exec(self, context_root: ContextRoot, data: dict) -> CommandResult:
                return CommandResult(context_root.Context.Name, False)

#-----------------------------------------------------------------------------------------------------#

class ContextNewCommandData (BaseModel):
    text: str = Field (
        description = "Название нового контекста"
    )

#-----------------------------------------------------------------------------------------------------#

class ContextNewCommand(Command):
    def __init__(self):
        super().__init__("Создай новый контекст", ContextNewCommandData)

    def exec(self, context_root: ContextRoot, data: dict) -> CommandResult:
        new_context = Context(data.get("text", "Новый контекст"))
        if new_context.Name == "":
            new_context.Name = "Новый контекст"
        context_root.Context = new_context
        return CommandResult(f"Создан новый контекст: {new_context.Name}", False)

#-----------------------------------------------------------------------------------------------------#

class LastResultCommand(Command):
    def __init__(self):
        super().__init__("Покажи последний результат")

    def exec(self, context_root: ContextRoot, data: dict) -> CommandResult:
        return CommandResult(f"Последний результат :\n {context_root.Context.lastResult}", False)

#-----------------------------------------------------------------------------------------------------#

class VariablesListCommand(Command):
    def __init__(self):
        super().__init__("Покажи список переменных")

    def exec(self, ctx: ContextRoot, data: dict) -> CommandResult:

        #logger.ingo("VariablesListCommand.exec:")
        res = ""
        for k in ctx.Context.knowledge:
            if res != "":
                res += f", \n"
            res += k.name

        return CommandResult(f"Список переменных :\n {res}", False)

#-----------------------------------------------------------------------------------------------------#

class VariablesCommandsParameters(BaseModel):
    name: str = Field (
        description = "Название переменной"
    )

#-----------------------------------------------------------------------------------------------------#

class ShowVariableCommand(Command):
    def __init__(self):
        super().__init__("Покажи переменную", VariablesCommandsParameters)

    def exec(self, ctx: ContextRoot, data: dict) -> CommandResult:
                var = data.get("name", "")
                knowledge = None
                for k in ctx.Context.knowledge:
                    if k.name == var:
                        knowledge = k
                res = "не найдено"
                if knowledge is not None:
                    res = knowledge.asText()
                return CommandResult(f"Значение переменной {var}:\n {res}")

#-----------------------------------------------------------------------------------------------------#

class SaveVariableCommand(Command):
    def __init__(self):
        super().__init__("Запомни последний результат как", VariablesCommandsParameters)

    def exec(self, ctx: ContextRoot, data: dict) -> CommandResult:
        var = data.get("name", "")
        knowledge = None
        for k in ctx.Context.knowledge:
            if k.name == var:
                knowledge = k

        if knowledge is not None:
            knowledge.text = ctx.Context.lastResult
        else:
            knowledge = TextKnowledge(var, ctx.Context.lastResult)
            ctx.Context.knowledge.append(knowledge)

        return CommandResult(f"Переменная '{var}' сохранена.", False)

#-----------------------------------------------------------------------------------------------------#

class VariablesCommandsParameters(BaseModel):
    name: str = Field (
        description = "Название переменной, под которой нужно сохранить текст"
    )
    text: str = Field (
        description = "Текст который нужно сохранить"
    )

class SaveTextAsVariableCommand(Command):
    def __init__(self):
        super().__init__("Запомни текст как", VariablesCommandsParameters)

    def exec(self, ctx: ContextRoot, data: dict) -> CommandResult:

        logger.info("SaveTextAsVariableCommand.exec:")

        var = data.get("name", "")
        text = data.get("text", "")

        logger.info(f"Исходные данные: {data}")

        #print (f"Название: {var}")
        #print (f"текст: {text}")
        knowledge = None

        for k in ctx.Context.knowledge:
            if k.name == var:
                knowledge = k

        if knowledge is not None:
            logger.info(f"Найдена переменная: {k.name}")
            knowledge.text = text
        else:
            logger.info(f"Создана переменная: {var}")
            knowledge = TextKnowledge(var, text)
            ctx.Context.knowledge.append(knowledge)

        return CommandResult(f"Переменная '{var}' сохранена.", False)

#-----------------------------------------------------------------------------------------------------#

class AddVariablesToLastResult(Command):
    def __init__(self):
        super().__init__("Подставь переменные в последний результат", VariablesCommandsParameters)

    def exec(self, ctx: ContextRoot, data: dict) -> CommandResult:

        res = ctx.Context.lastResult
        res = fillKnowledge(ctx, res)

        return CommandResult(res)

#-----------------------------------------------------------------------------------------------------#

class AddLastResultToVariableCommandParameters(BaseModel):
    name: str = Field (
        description = "Название переменной, к которой надо добавить последний результат"
    )

class AddLastResultToVariableCommand(Command):
    def __init__(self):
        super().__init__("Добавь к переменной", AddLastResultToVariableCommandParameters)

    def exec(self, ctx: ContextRoot, data: dict) -> CommandResult:

        logger.info("AddLastResultToVariableCommand.exec:")

        var = data.get("name", "")

        logger.info(f"Исходные данные: {data}")
        logger.info(f"Последний результат: {ctx.Context.lastResult}")

        #print (f"Название: {var}")
        #print (f"текст: {text}")
        knowledge = None

        for k in ctx.Context.knowledge:
            if k.name == var:
                knowledge = k

        if knowledge is not None:
            knowledge.text = knowledge.text + " \n" + ctx.Context.lastResult

        else:
            knowledge = TextKnowledge(var, ctx.Context.lastResult)
            ctx.Context.knowledge.append(knowledge)

        return CommandResult(f"Переменная '{var}' обновлена.", False)

#-----------------------------------------------------------------------------------------------------#

def RegisterContextCommands(cp: CommandProcessor):
    cp.Commands.append(ContextShowCommand())
    cp.Commands.append(ContextNewCommand())
    cp.Commands.append(LastResultCommand())
    cp.Commands.append(ShowVariableCommand())
    cp.Commands.append(SaveVariableCommand())
    cp.Commands.append(VariablesListCommand())
    cp.Commands.append(SaveTextAsVariableCommand())
    cp.Commands.append(AddLastResultToVariableCommand())
    cp.Commands.append(AddVariablesToLastResult())
