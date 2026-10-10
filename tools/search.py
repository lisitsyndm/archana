#
#   DEPRECATED
#

from core.command import Command
from core.command_result import CommandResult
from core.context import Context
from core.context_root import ContextRoot
from core.command_processor import CommandProcessor
from pydantic import BaseModel, Field
from core.knowledge import TextKnowledge

class SearchCommandParameters(BaseModel):
    query: str = Field (
            description = "Поисковый запрос (что надо искать)"
        )
    documents_count: int = Field (
            description = "Количество документов, которые надо просмотреть"
        )
    save_to: str = Field (
            description = "Результат сохранить как"
    )

class SearchCommand(Command):
    def __init__(self):
        super().__init__("Найди в интернете", SearchCommandParameters)

    def exec(self, context_root: ContextRoot, data: dict) -> CommandResult:
        res = "Postgres, MySQL, SQLLite, MS SQL Server, Oracle"
        kn = TextKnowledge(res, "Реляционные базы данных")
        return CommandResult(res)

def RegisterSearchCommands(cp: CommandProcessor):
    cp.Commands.append(SearchCommand())