class DatabaseError(Exception):
    """Базовое исключение DAL."""
    pass


class KnowledgeNotFoundError(DatabaseError):
    """Запись в knowledge не найдена."""
    pass


class PlanNotFoundError(DatabaseError):
    """План не найден."""
    pass


class ConnectionError(DatabaseError):
    """Проблема с подключением к БД."""
    pass
