import sys
import codecs
from core.command_processor import CommandProcessor
from core.command_result import CommandResult
from core.tstdata import DATABASES, CRITERIA, SYSTEM_CONTEXT, COMPARISON, ADR
from core.user_data import UserData
from core.user_roles import UserRoles
from core.context_manager import ContextManager

class MessageService:
    def __init__(self):
        self.CommandProcessor: CommandProcessor = None
        self.CurrentMessage: str = ""
        self.should_continue = True
        self.CurrentUser: UserData = None

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

        # Аутентификация (один раз в начале)
        username = input("\nЛогин: ")
        password = input("Пароль: ")
        user_data = self._auth(username, password)
        self.CurrentUser = user_data

        if user_data is None:
            print("Доступ запрещён.")
            return

        # Получение контекста пользователя
        ctx_root = ContextManager().get_context(user_data.ID)
        ctx_root.User = user_data
        self.CommandProcessor.ctx_root = ctx_root

        # Цикл обработки команд
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

    def _auth(self, username: str, password: str) -> UserData | None:
        """Аутентификация пользователя."""
        if username == "admin":
            return UserData(ID="admin", Roles=UserRoles.admin)
        elif username == "unauthorized":
            return None
        else:
            return UserData(ID="user", Roles=UserRoles.user)

    def handle_result(self, result: CommandResult):
        print(f"\nБот: {result.output_text}")
        self.should_continue = result.should_continue