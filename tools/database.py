import os
from dotenv import load_dotenv

from core.command import Command
from core.command_result import CommandResult
from core.context_root import ContextRoot
from core.command_processor import CommandProcessor
from core.user_roles import UserRoles
from pydantic import BaseModel, Field
from llm.embedder_client import EmbedderClient

from data.pg_repository import PostgresKnowledgeRepository

load_dotenv()

# Singleton repository instance
_knowledge_repo = None


def _get_knowledge_repo() -> PostgresKnowledgeRepository:
    global _knowledge_repo
    if _knowledge_repo is None:
        _knowledge_repo = PostgresKnowledgeRepository()
    return _knowledge_repo


#-----------------------------------------------------------------------------------------------------#

class LoadFromDatabaseCommandParameters(BaseModel):
    query: str = Field(
        description="Запрос для поиска"
    )


class LoadFromDatabaseCommand(Command):
    def __init__(self):
        super().__init__("Найди в БД", LoadFromDatabaseCommandParameters, required_role=UserRoles.user)

    def exec(self, ctx: ContextRoot, data: dict) -> CommandResult:
        query = data.get("query", "")

        if query == "":
            return CommandResult("Запрос не содержит данных")

        # Генерируем эмбеддинг для поискового запроса
        query_embedding = EmbedderClient.get_instance().generate_embedding(query)

        repo = _get_knowledge_repo()
        result = repo.search(query_embedding)

        if result:
            return CommandResult(result, True)
        else:
            return CommandResult("Ничего не найдено", True)


#-----------------------------------------------------------------------------------------------------#

class SaveToDatabaseCommandParameters(BaseModel):
    name: str = Field(
        description="Названия для сохраняемой информации (ключ)"
    )
    text: str = Field(
        description="Сохраняемая информация"
    )


class SaveToDatabaseCommand(Command):
    def __init__(self):
        super().__init__("Сохрани в БД", SaveToDatabaseCommandParameters, required_role=UserRoles.admin)

    def exec(self, ctx: ContextRoot, data: dict) -> CommandResult:
        name = data.get("name", "")
        text = data.get("text", "")

        if name == "":
            return CommandResult("Название информации (ключ) пустой.")

        if text == "":
            return CommandResult("Информация для сохранения отсутствует.")

        # Генерируем эмбеддинг
        embedding = EmbedderClient.get_instance().generate_embedding(name)

        repo = _get_knowledge_repo()
        repo.upsert(name, text, embedding)

        return CommandResult("Информация сохранена.", False)


#-----------------------------------------------------------------------------------------------------#

def RegisterDatabaseCommands(cp: CommandProcessor):
    cp.Commands.append(LoadFromDatabaseCommand())
    cp.Commands.append(SaveToDatabaseCommand())
