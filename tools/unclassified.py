import os
from dotenv import load_dotenv

from core.command import Command
from core.command_result import CommandResult
from core.context import Context
from core.context_root import ContextRoot
from pydantic import BaseModel, Field
from core.knowledge import Knowledge, TextKnowledge
from langchain_openai import ChatOpenAI
import time
from observability.metrics import llm_inference_command_duration_seconds, llm_tokens_total

load_dotenv()

#-----------------------------------------------------------------------------------------------------#

APIKEY = os.getenv("LLM_APIKEY", "")
MODEL = os.getenv("LLM_MODEL", "gpt-4.1-nano")
URL = os.getenv("LLM_URL", "https://api.aitunnel.ru/v1/")

#-----------------------------------------------------------------------------------------------------#

class UnclassifiedCommandData (BaseModel):
    text: str = Field (
        description = "Промпт"
    )

class UnclassifiedCommand(Command):
    llm = ChatOpenAI(
        model= MODEL,
        api_key = APIKEY,
        base_url = URL,
        temperature = 0,
        request_timeout = 60,
        max_retries = 3,
        )

    def __init__(self):
        super().__init__("Вызов LLM", UnclassifiedCommandData)

    def exec(self, context_root: ContextRoot, data: dict) -> CommandResult:
        start_time = time.time()
        prompt = data.get("text", "")

        prompt_test = prompt.replace("\n", "").replace("\r", "").strip()
        if prompt_test == "": return CommandResult("Текст промпта не заполнен!", False)

        if prompt is None:
            return CommandResult("Промпт отсутствует!")

        if prompt == "":
            return CommandResult("Промпт отсутствует!")

        response = self.llm.invoke(prompt)
        res = response.content

        duration = time.time() - start_time
        llm_inference_command_duration_seconds.observe(duration)

        # Получаем информацию о токенах
        try:
            usage = response.response_metadata.get('token_usage', {})
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)

            llm_tokens_total.labels(type="prompt").inc(prompt_tokens)
            llm_tokens_total.labels(type="completion").inc(completion_tokens)
        except (AttributeError, KeyError):
            pass

        return CommandResult(res)

#-----------------------------------------------------------------------------------------------------#

def RegisterUnclassifiedCommands(ctx: ContextRoot):
    ctx.Commands.append(UnclassifiedCommand())