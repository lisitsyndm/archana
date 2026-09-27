from core.command import Command
from core.command_result import CommandResult
from core.context import Context
from core.context_root import ContextRoot
from pydantic import BaseModel, Field
from core.knowledge import Knowledge, TextKnowledge


class SaveToFileCommandParameters(BaseModel):
    path: str = Field(
        description="Имя и путь к файлу"
    )


class SaveToFileCommand(Command):
    def __init__(self):
        super().__init__("Сохрани последний результат в файл", SaveToFileCommandParameters)

    def exec(self, ctx: ContextRoot, data: dict) -> CommandResult:
        res = ctx.Context.lastResult
        path = data.get("path", "")

        with open(path, "w", encoding="utf-8") as f:
            f.write(res)

        return CommandResult("Данные сохранены в файл: {path}", False)


def RegisterFileCommands(ctx: ContextRoot):
    ctx.Commands.append(SaveToFileCommand())
