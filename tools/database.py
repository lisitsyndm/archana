import os
from dotenv import load_dotenv

import psycopg2

from core.command import Command
from core.command_result import CommandResult
from core.context import Context
from core.context_root import ContextRoot
from pydantic import BaseModel, Field
from core.knowledge import Knowledge, TextKnowledge
from core.embeddings import generate_embedding

load_dotenv()

#-----------------------------------------------------------------------------------------------------#

def embedding_to_vector(embedding: list[float]) -> str:
    """Конвертирует список float в строковый формат для pgvector."""
    return "[" + ",".join(f"{x:.8f}" for x in embedding) + "]"

#-----------------------------------------------------------------------------------------------------#

class LoadFromDatabaseCommandParameters(BaseModel):
    query: str = Field(
        description="Запрос для поиска"
    )

class LoadFromDatabaseCommand(Command):
    def __init__(self):
        super().__init__("Найди в БД", LoadFromDatabaseCommandParameters)

    def exec(self, ctx: ContextRoot, data: dict) -> CommandResult:
        res = ""
        query = data.get("query", "")

        if query == "":
            return CommandResult("Запрос не содержит данных")

        # Генерируем эмбеддинг для поискового запроса
        query_embedding = generate_embedding(query)

        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "knowledge"),
            user=os.getenv("DB_USERNAME", ""),
            password=os.getenv("DB_PASSWORD", "")
        )
        cursor = conn.cursor()
        
        # Семантический поиск через косинусово сходство pgvector
        # Максимальное косинусное расстояние (задаётся в .env)
        MAX_COSINE_DISTANCE = float(os.getenv("MAX_COSINE_DISTANCE", "0.25"))
        query_vector = embedding_to_vector(query_embedding)
        cursor.execute(
            "SELECT text FROM knowledge "
            "WHERE embedding IS NOT NULL "
            "AND embedding <=> %s::vector <= %s "
            "ORDER BY embedding <=> %s::vector "
            "LIMIT 1",
            (query_vector, MAX_COSINE_DISTANCE, query_vector)
        )
        row = cursor.fetchone()
        
        if row:
            res = row[0]
        else:
            res = "Ничего не найдено"
            
        cursor.close()
        conn.close()

        return CommandResult(res, True)

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
        super().__init__("Сохрани в БД", SaveToDatabaseCommandParameters)

    def exec(self, ctx: ContextRoot, data: dict) -> CommandResult:
        res = ""
        name = data.get("name", "")
        text = data.get("text", "")

        if name == "":
            return CommandResult("Название информации (ключ) пустой.")

        if text == "":
            return CommandResult("Информация для сохранения отсутствует.")

        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "knowledge"),
            user=os.getenv("DB_USERNAME", ""),
            password=os.getenv("DB_PASSWORD", "")
        )
        cursor = conn.cursor()
        # Генерируем эмбеддинг
        embedding = generate_embedding(name)
        embedding_vector = embedding_to_vector(embedding)

        cursor.execute(
            "INSERT INTO knowledge (name, text, embedding) VALUES (%s, %s, %s::vector) "
            "ON CONFLICT (name) DO UPDATE SET text = EXCLUDED.text, embedding = EXCLUDED.embedding",
            (name, text, embedding_vector)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return CommandResult("Информация сохранена.", False)

#-----------------------------------------------------------------------------------------------------#

def RegisterDatabaseCommands(ctx: ContextRoot):
    ctx.Commands.append(LoadFromDatabaseCommand())
    ctx.Commands.append(SaveToDatabaseCommand())
