import os
import logging
import time
from typing import Any, Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from observability.metrics import (
    llm_classification_duration_seconds,
    llm_data_prep_duration_seconds,
    llm_inference_command_duration_seconds,
    llm_tokens_total,
)

load_dotenv()

logger = logging.getLogger(__name__)

APIKEY = os.getenv("LLM_APIKEY", "")
MODEL = os.getenv("LLM_MODEL", "gpt-4.1-nano")
URL = os.getenv("LLM_URL", "https://api.aitunnel.ru/v1/")


class LLMClient:
    """Клиент для LLM chat completions."""

    _instance: Optional["LLMClient"] = None
    _initialized: bool = False

    def __init__(self):
        if LLMClient._initialized:
            return

        self._chat = ChatOpenAI(
            model=MODEL,
            api_key=APIKEY,
            base_url=URL,
            temperature=0,
            request_timeout=60,
            max_retries=3,
        )
        LLMClient._initialized = True

    @classmethod
    def get_instance(cls) -> "LLMClient":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def invoke(self, prompt: str, metric_name: str = "llm_inference") -> str:
        """Простой вызов LLM, возвращает content ответа."""
        start_time = time.time()

        response = self._chat.invoke(prompt)

        duration = time.time() - start_time
        self._track_duration(metric_name, duration)
        self._track_tokens(response)

        return response.content.strip()

    def invoke_with_parser(
        self,
        prompt_template: PromptTemplate,
        parser: JsonOutputParser,
        fields: str,
        user_input: str,
        metric_name: str = "llm_data_prep",
    ) -> Any:
        """Вызов LLM с парсером вывода (chain: prompt | llm | parser)."""
        start_time = time.time()

        classification_chain = prompt_template | self._chat | parser

        formatted_prompt = prompt_template.format(
            fields=fields,
            user_input=user_input,
            format_instructions=parser.get_format_instructions(),
        )
        logger.info(f"Промпт для LLM:\n{formatted_prompt}")

        payload = classification_chain.invoke(
            {
                "fields": fields,
                "user_input": user_input,
                "format_instructions": parser.get_format_instructions(),
            }
        )

        duration = time.time() - start_time
        self._track_duration(metric_name, duration)
        self._track_tokens(payload)

        return payload

    def _track_tokens(self, response: Any) -> None:
        """Подсчёт токенов из ответа LLM."""
        try:
            usage = response.response_metadata.get("token_usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)

            llm_tokens_total.labels(type="prompt").inc(prompt_tokens)
            llm_tokens_total.labels(type="completion").inc(completion_tokens)
        except (AttributeError, KeyError):
            logger.warning("Не удалось получить информацию о токенах")

    def _track_duration(self, metric_name: str, duration: float) -> None:
        """Запись метрики длительности."""
        metric_map = {
            "llm_classification": llm_classification_duration_seconds,
            "llm_data_prep": llm_data_prep_duration_seconds,
            "llm_inference": llm_inference_command_duration_seconds,
        }
        metric = metric_map.get(metric_name)
        if metric:
            metric.observe(duration)
