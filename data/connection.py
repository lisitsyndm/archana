import os
from dotenv import load_dotenv
from psycopg2.pool import ThreadedConnectionPool
from typing import Optional

from data.exceptions import ConnectionError

load_dotenv()

_pool: Optional[ThreadedConnectionPool] = None


def get_connection_params() -> dict:
    """Единый источник DB-конфигурации из env."""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "database": os.getenv("DB_NAME", "knowledge"),
        "user": os.getenv("DB_USERNAME", "postgres"),
        "password": os.getenv("DB_PASSWORD", "postgres"),
    }


def create_pool(min_connections: int = 1, max_connections: int = 10) -> ThreadedConnectionPool:
    """Создаёт connection pool."""
    global _pool
    params = get_connection_params()
    try:
        _pool = ThreadedConnectionPool(
            minconn=min_connections,
            maxconn=max_connections,
            **params,
        )
    except Exception as e:
        raise ConnectionError(f"Не удалось создать пул подключений: {e}") from e
    return _pool


def get_pool() -> ThreadedConnectionPool:
    """Singleton pool (lazy init)."""
    global _pool
    if _pool is None:
        _pool = create_pool()
    return _pool


def close_pool() -> None:
    """Закрывает connection pool."""
    global _pool
    if _pool is not None:
        _pool.closeall()
        _pool = None
