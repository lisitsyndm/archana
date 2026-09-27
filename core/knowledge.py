from typing import List


class Knowledge:
    def __init__(self, name):
        self.name = name

    def asText(self):
        return ""

class TextKnowledge(Knowledge):
    def __init__(self, name, text):
        super().__init__(name)
        self.text = text

    def asText(self):
        return self.text

class Entity(Knowledge):
    def __init__(self, name: str, type: str):
        self.name = name
        self.type = type

class KnowledgeList(Knowledge):
    def __init__(self):
        self.list: List[Knowledge] = []
