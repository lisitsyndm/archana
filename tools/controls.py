from core.command import Command
from core.command_result import CommandResult
from core.context import Context
from core.context_root import ContextRoot
from core.command_processor import CommandProcessor

class ExitCommand(Command):
    def __init__(self):
        super().__init__(name="Выход")

    def exec(self, context_root: ContextRoot, data: dict) -> CommandResult:
        return CommandResult("Работа завершена", False,False)

def RegisterControlCommands(cp: CommandProcessor):
    cp.Commands.append(ExitCommand())