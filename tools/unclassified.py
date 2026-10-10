import os
from dotenv import load_dotenv

from core.command import Command
from core.command_result import CommandResult
from core.context import Context
from core.context_root import ContextRoot
from core.command_processor import CommandProcessor
from llm.llm_client import LLMClient
from pydantic import BaseModel, Field
from core.knowledge import Knowledge, TextKnowledge
import time
from observability.metrics import llm_inference_command_duration_seconds, llm_tokens_total

load_dotenv()

#-----------------------------------------------------------------------------------------------------#

class UnclassifiedCommandData (BaseModel):
    text: str = Field (
        description = "Промпт"
    )

class UnclassifiedCommand(Command):
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

        response = LLMClient.get_instance().invoke(prompt, metric_name="llm_inference")

        duration = time.time() - start_time
        llm_inference_command_duration_seconds.observe(duration)

        return CommandResult(response)

#-----------------------------------------------------------------------------------------------------#

def RegisterUnclassifiedCommands(cp: CommandProcessor):
    cp.Commands.append(UnclassifiedCommand())
