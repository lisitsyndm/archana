import os
import logging
import requests

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from core.command import Command
from core.command_result import CommandResult
from core.context import Context
from core.context_root import ContextRoot
from core.command_processor import CommandProcessor
from core.logger import *

logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = os.getenv("YANDEX_API_KEY", "")
FOLDER_ID = os.getenv("YANDEX_FOLDER_ID", "")
API_URL = os.getenv("YANDEX_API_URL", "")


class InternetSearchCommandParameters(BaseModel):
    text: str = Field(
        description="Поисковый запрос. В него надо поместить весь текст сообшения."
    )


class InternetSearchCommand(Command):
    def __init__(self):
        super().__init__("Найти в интернете", InternetSearchCommandParameters)

    def exec(self, ctx: ContextRoot, data: dict) -> CommandResult:

        logger.info(f"InternetSearchCommand.exec:")
        res = ""
        query = data.get("text", "")

        if query == "":
            return CommandResult("Запрос пустой")

        payload = {
            "messages": [
                {
                    "content": query,
                    "role": "ROLE_USER"
                }
            ],
            "folderId": FOLDER_ID,
            "fixMisspell": "true",
            "enableNrfmDocs": "false",
            "enableRichStructuredAnswer": True,
            "getPartialResults": False
        }

        headers = {
            "Authorization": f"Api-Key {API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(API_URL, json=payload, headers=headers)

        logger.info(f"Статус ответа: {response.status_code}")
        logger.info(f"Response: {response}")


        #print(response.json())
        data = response.json()

        logger.info(f"Data: {data}")

        # Извлекаем content из первого элемента массива
        if isinstance(data, list) and len(data) > 0:
            first_item = data[0]
            if isinstance(first_item, dict) and "message" in first_item:
                res = first_item["message"].get("content", "")
            else:
                res = ""
        else:
            res = ""

        return CommandResult(res)


def RegisterResearcherCommands(cp: CommandProcessor):
    cp.Commands.append(InternetSearchCommand())
