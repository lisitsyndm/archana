import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")


def generate_embedding(text: str) -> list[float]:
    """Генерирует эмбеддинг текста через OpenAI API.
    
    Args:
        text: Текст для генерации эмбеддинга
        
    Returns:
        Список float значений эмбеддинга (1536 для text-embedding-3-small)
    """
    client = OpenAI(
        api_key=os.getenv("LLM_APIKEY"),
        base_url=os.getenv("LLM_URL", "https://api.aitunnel.ru/v1/")
    )
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding
