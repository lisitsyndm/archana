import os
import logging
import time
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

from observability.metrics import llm_tokens_total

load_dotenv()

EMBEDDING_APIKEY = os.getenv("EMBEDDING_APIKEY", "")
EMBEDDING_URL = os.getenv("EMBEDDING_URL", "https://api.aitunnel.ru/v1/")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

logger = logging.getLogger(__name__)


class EmbedderClient:
    """Клиент для генерации эмбеддингов."""

    _instance: Optional["EmbedderClient"] = None
    _initialized: bool = False

    def __init__(self):
        if EmbedderClient._initialized:
            return

        self._client = OpenAI(
            api_key=EMBEDDING_APIKEY or os.getenv("LLM_APIKEY", ""),
            base_url=EMBEDDING_URL,
        )
        EmbedderClient._initialized = True

    @classmethod
    def get_instance(cls) -> "EmbedderClient":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def generate_embedding(self, text: str) -> list[float]:
        """Генерирует эмбеддинг текста через OpenAI-compatible API.

        Args:
            text: Текст для генерации эмбеддинга

        Returns:
            Список float значений эмбеддинга
        """
        response = self._client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text,
        )
        return response.data[0].embedding
