from typing import Dict
from core.context_root import ContextRoot


class _ContextManagerSingleton:
    """Синглтон для управления контекстами пользователей."""

    def __init__(self):
        self._contexts: Dict[str, ContextRoot] = {}

    def get_context(self, user_id: str) -> ContextRoot:
        """Возвращает ContextRoot для пользователя.
        
        Если контекст для данного user_id ещё не создан, создаёт новый.
        
        Args:
            user_id: Уникальный идентификатор пользователя (строка).
            
        Returns:
            ContextRoot, привязанный к user_id.
        """
        if user_id not in self._contexts:
            self._contexts[user_id] = ContextRoot(name=f"Context for {user_id}")
        return self._contexts[user_id]


class ContextManager:
    """Фасад для доступа к синглтону ContextManager."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._manager = _ContextManagerSingleton()
        return cls._instance

    def get_context(self, user_id: str) -> ContextRoot:
        """Возвращает ContextRoot для пользователя.
        
        Если контекст для данного user_id ещё не создан, создаёт новый.
        
        Args:
            user_id: Уникальный идентификатор пользователя (строка).
            
        Returns:
            ContextRoot, привязанный к user_id.
        """
        return self._manager.get_context(user_id)
