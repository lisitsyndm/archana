import os
from dotenv import load_dotenv
from typing import List, Optional

from data.repository import KnowledgeRepository, PlanRepository
from data.connection import get_pool
from data.exceptions import ConnectionError, KnowledgeNotFoundError, PlanNotFoundError

from core.command_data import CommandData

load_dotenv()


def _embedding_to_vector(embedding: list[float]) -> str:
    """Конвертирует список float в строковый формат для pgvector."""
    return "[" + ",".join(f"{x:.8f}" for x in embedding) + "]"


class PostgresKnowledgeRepository(KnowledgeRepository):
    """Реализация KnowledgeRepository для PostgreSQL."""

    def search(self, query_embedding: list[float], limit: int = 1) -> Optional[str]:
        pool = get_pool()
        if pool is None:
            raise ConnectionError("Connection pool not initialized")

        conn = None
        cursor = None
        try:
            conn = pool.getconn()
            cursor = conn.cursor()

            MAX_COSINE_DISTANCE = float(os.getenv("MAX_COSINE_DISTANCE", "0.25"))
            query_vector = _embedding_to_vector(query_embedding)

            cursor.execute(
                "SELECT text FROM knowledge "
                "WHERE embedding IS NOT NULL "
                "AND embedding <=> %s::vector <= %s "
                "ORDER BY embedding <=> %s::vector "
                "LIMIT 1",
                (query_vector, MAX_COSINE_DISTANCE, query_vector),
            )
            row = cursor.fetchone()

            if row:
                return row[0]
            return None
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                pool.putconn(conn)

    def upsert(self, name: str, text: str, embedding: list[float]) -> None:
        pool = get_pool()
        if pool is None:
            raise ConnectionError("Connection pool not initialized")

        conn = None
        cursor = None
        try:
            conn = pool.getconn()
            cursor = conn.cursor()

            embedding_vector = _embedding_to_vector(embedding)

            cursor.execute(
                "INSERT INTO knowledge (name, text, embedding) VALUES (%s, %s, %s::vector) "
                "ON CONFLICT (name) DO UPDATE SET text = EXCLUDED.text, embedding = EXCLUDED.embedding",
                (name, text, embedding_vector),
            )
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                pool.putconn(conn)


class PostgresPlanRepository(PlanRepository):
    """Реализация PlanRepository для PostgreSQL."""

    def get_by_id_or_name(self, identifier: str) -> Optional[dict]:
        pool = get_pool()
        if pool is None:
            raise ConnectionError("Connection pool not initialized")

        conn = None
        cursor = None
        try:
            conn = pool.getconn()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, name FROM \"Plan\" WHERE id = %s OR name = %s",
                (identifier, identifier),
            )
            row = cursor.fetchone()
            if row is None:
                return None

            plan_id = row[0]

            cursor.execute(
                "SELECT commandName, commandPayload FROM \"PlanItem\" WHERE plan_id = %s ORDER BY number",
                (plan_id,),
            )
            items = cursor.fetchall()

            return {"plan_id": plan_id, "items": items}
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                pool.putconn(conn)

    def save(self, name: str, commands: List[CommandData]) -> int:
        pool = get_pool()
        if pool is None:
            raise ConnectionError("Connection pool not initialized")

        conn = None
        cursor = None
        try:
            conn = pool.getconn()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO \"Plan\" (name) VALUES (%s) "
                "ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name "
                "RETURNING id",
                (name,),
            )
            plan_id = cursor.fetchone()[0]

            cursor.execute(
                "DELETE FROM \"PlanItem\" WHERE plan_id = %s",
                (plan_id,),
            )

            for idx, cmd in enumerate(commands, start=1):
                cursor.execute(
                    "INSERT INTO \"PlanItem\" (number, plan_id, commandName, commandPayload) "
                    "VALUES (%s, %s, %s, %s)",
                    (idx, plan_id, cmd.commandName, cmd.commandPayload),
                )

            conn.commit()
            return plan_id
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                pool.putconn(conn)
