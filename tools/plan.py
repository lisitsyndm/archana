from core.command import Command
from core.command_result import CommandResult
from core.command_data import CommandData
from core.context import Context
from core.context_root import ContextRoot
from core.command_processor import CommandProcessor
from pydantic import BaseModel, Field
from core.knowledge import Knowledge, TextKnowledge
from core.helpers import fillKnowledge

#-----------------------------------------------------------------------------------------------------#

class ExecutePlanTool(Command):
    def __init__(self):
        super().__init__("Выполни план")

    def exec(self, ctx: ContextRoot, data: dict) -> CommandResult:
        ctx.plan.restart()
        return CommandResult("Выполнение плана начато", False)

#-----------------------------------------------------------------------------------------------------#

class ResetPlanTool(Command):
    def __init__(self):
        super().__init__("Удали план")

    def exec(self, ctx: ContextRoot, data: dict) -> CommandResult:
        ctx.plan.reset()
        return CommandResult("Готова начать план с начала", False)

#-----------------------------------------------------------------------------------------------------#

class ContinuePlanTool(Command):
    def __init__(self):
        super().__init__("Продолжи выполнение плана")

    def exec(self, ctx: ContextRoot, data: dict) -> CommandResult:
        ctx.plan.proceed()
        return CommandResult("План продолжен", False)

#-----------------------------------------------------------------------------------------------------#

class PausePlanTool(Command):
    def __init__(self):
        super().__init__("Останови выполнение плана")

    def exec(self, ctx: ContextRoot, data: dict) -> CommandResult:
        ctx.plan.pause()
        return CommandResult("Выполнение плана приостановлено", False)

#-----------------------------------------------------------------------------------------------------#


class PlanToolParameters(BaseModel):
    name: str = Field (
        description = "Название плана"
    )

#-----------------------------------------------------------------------------------------------------#

class LoadPlanFromDBTool(Command):
    def __init__(self):
        super().__init__("Загрузи план из базы данных", PlanToolParameters)

    def exec(self, ctx: ContextRoot, data: dict) -> CommandResult:
        ctx.plan.loadFromDatabase(data.get("name", ""))
        return CommandResult("План загружен", False)

#-----------------------------------------------------------------------------------------------------#

class SavePlanToDBTool(Command):
    def __init__(self):
        super().__init__("Сохрани план в базу данных", PlanToolParameters)

    def exec(self, ctx: ContextRoot, data: dict) -> CommandResult:
        ctx.plan.saveToDatabase(data.get("name", ""))
        return CommandResult("План сохранен", False)

#-----------------------------------------------------------------------------------------------------#

class SaveLastHistoryItemToPlanTool(Command):
    def __init__(self):
        super().__init__("Сохрани последнюю команду в план")

    def exec(self, ctx: ContextRoot, data: dict) -> CommandResult:
        import copy

        if not ctx.histories:
            return CommandResult("История пуста")

        last_command = None
        
        for item in reversed(ctx.histories):
            if isinstance(item, CommandData):
                last_command = item
                break

        if last_command is None:
            return CommandResult("В истории нет команд типа CommandData")

        last_command = copy.deepcopy(last_command)
        ctx.plan.commands.append(last_command)

        return CommandResult("Команда сохранена в план", False)

#-----------------------------------------------------------------------------------------------------#

class ShowPlanTool(Command):
    def __init__(self):
        super().__init__("Покажи план")

    def exec(self, ctx: ContextRoot, data: dict) -> CommandResult:
        res = "Печатаю план:\n"

        for item in ctx.plan.commands:
            if isinstance(item, CommandData):
                res += "------------\n"
                res += f"commandName: {item.commandName}\n"
                res += f"commandPayload: {item.commandPayload}\n"

        return CommandResult(res, False)
#-----------------------------------------------------------------------------------------------------#

def RegisterPlanCommands(cp: CommandProcessor):
    cp.Commands.append(ExecutePlanTool())
    cp.Commands.append(ResetPlanTool())

    cp.Commands.append(ContinuePlanTool())
    cp.Commands.append(PausePlanTool())
    cp.Commands.append(LoadPlanFromDBTool())
    cp.Commands.append(SavePlanToDBTool())
    cp.Commands.append(SaveLastHistoryItemToPlanTool())
    cp.Commands.append(ShowPlanTool())


