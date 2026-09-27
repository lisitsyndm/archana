class CommandData:
    textVersion: str
    commandName: str
    commandPayload: str

    @classmethod
    def createFromText(cls, text: str) -> "CommandData":
        instance = cls()
        instance.textVersion = text
        return instance

    @classmethod
    def createFromStructuredData(cls, command_name: str, command_payload: str) -> "CommandData":
        instance = cls()
        instance.commandName = command_name
        instance.commandPayload = command_payload
        return instance
