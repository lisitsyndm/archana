class LLMToolNotFoundError(Exception):
    def __init__(self):
        super().__init__("LLM Tool не найден. Подключение этого инструмента является обязательным для работы.")