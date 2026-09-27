import sys
import codecs
from core.command_processor import CommandProcessor
from core.command_result import CommandResult
from core.tstdata import DATABASES, CRITERIA, SYSTEM_CONTEXT, COMPARISON, ADR

class MessageService:
    def __init__(self):
        self.CommandProcessor: CommandProcessor = None
        self.CurrentMessage: str = ""
        self.should_continue = True

    def _read_input(self):
        """Read input with fallback encoding for Windows terminals."""
        try:
            return input("\nВы: ")
        except UnicodeDecodeError:
            # Fallback: read directly from stdin with cp1251 encoding
            raw = sys.stdin.buffer.readline()
            return raw.decode('cp1251', errors='replace')

    def Run(self):
        self.should_continue = True
        while self.should_continue:
            text = self._read_input()
            self.CurrentMessage = text
            self.CommandProcessor.process(text, self.handle_result)

    def Prepare(self):
        self.CommandProcessor.process(DATABASES, self.handle_result)
        self.CommandProcessor.process(CRITERIA, self.handle_result)
        self.CommandProcessor.process(SYSTEM_CONTEXT, self.handle_result)
        self.CommandProcessor.process(COMPARISON, self.handle_result)
        self.CommandProcessor.process(ADR, self.handle_result)

    def handle_result(self, result: CommandResult):
        print(f"\nБот: {result.output_text}")
        self.should_continue = result.should_continue