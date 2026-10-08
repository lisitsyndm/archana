import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import MagicMock, patch
from data.exceptions import DatabaseError, KnowledgeNotFoundError, PlanNotFoundError, ConnectionError


class TestExceptions(unittest.TestCase):
    """Тесты для модуля exceptions."""

    def test_database_error_is_exception(self):
        self.assertTrue(issubclass(DatabaseError, Exception))

    def test_knowledge_not_found_error_inherits_database_error(self):
        self.assertTrue(issubclass(KnowledgeNotFoundError, DatabaseError))

    def test_plan_not_found_error_inherits_database_error(self):
        self.assertTrue(issubclass(PlanNotFoundError, DatabaseError))

    def test_connection_error_inherits_database_error(self):
        self.assertTrue(issubclass(ConnectionError, DatabaseError))


if __name__ == "__main__":
    unittest.main()
