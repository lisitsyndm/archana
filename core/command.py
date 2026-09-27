import json
#from context.context_root import ContextRoot
from core.command_result import CommandResult
from core.command_data import CommandData
from langchain_core.prompts import PromptTemplate


class Command:
    def __init__(self, name: str = "", data_class = None):
        self.Name = name[:256] if len(name) > 256 else name
        self.TechName = " ".join(self.Name.lower().split())
        self.Text = ""
        self.Data = {}
        self.data_class = data_class

    def Parse(self, payload: str):
        try:
            #print ("преобразуем строку в Json")
            payload = str(payload).replace("\n", "\\n").replace("\r", "\\r")
            self.Data = json.loads(payload)
        except json.JSONDecodeError as e:
            #print(f"Ошибка парсинга JSON: {e}")
            self.Data = {"text": str(payload)}
        return self.Data

    def Execute(self, context_root) -> CommandResult:
        return CommandResult()

    def exec(self, context_root, data: dict) -> CommandResult:
        return CommandResult()


