from typing import List
from core.knowledge import Knowledge


class Context:
    knowledge : List[Knowledge] = []
    lastResult : str = ""

    def __init__(self, name=""):
        self.Name = name

    def getKnowledgeList(self):
        return [k.name for k in self.knowledge]

    def getKnowledgeTextByName(self, aname: str):
        for k in self.knowledge:
            if k.name.strip().lower() == aname.strip().lower():
                return k.asText()
        return None
