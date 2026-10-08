import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import MagicMock, patch, mock_open
from data.pg_repository import PostgresKnowledgeRepository, PostgresPlanRepository, _embedding_to_vector


class TestEmbeddingToVector(unittest.TestCase):
    """Тесты для утилиты _embedding_to_vector."""

    def test_converts_list_to_vector_string(self):
        result = _embedding_to_vector([0.1, 0.2, 0.3])
        self.assertEqual(result, "[0.10000000,0.20000000,0.30000000]")

    def test_empty_list(self):
        result = _embedding_to_vector([])
        self.assertEqual(result, "[]")

    def test_single_element(self):
        result = _embedding_to_vector([1.0])
        self.assertEqual(result, "[1.00000000]")


class TestPostgresKnowledgeRepository(unittest.TestCase):
    """Тесты для PostgresKnowledgeRepository."""

    def setUp(self):
        self.repo = PostgresKnowledgeRepository()

    @patch("data.pg_repository.get_pool")
    def test_search_returns_text_on_match(self, mock_get_pool):
        mock_pool = MagicMock()
        mock_get_pool.return_value = mock_pool

        mock_conn = MagicMock()
        mock_pool.getconn.return_value = mock_conn

        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ("Found text",)

        result = self.repo.search([0.1] * 1536)
        self.assertEqual(result, "Found text")
        mock_cursor.close.assert_called_once()
        mock_pool.putconn.assert_called_once()

    @patch("data.pg_repository.get_pool")
    def test_search_returns_none_on_no_match(self, mock_get_pool):
        mock_pool = MagicMock()
        mock_get_pool.return_value = mock_pool

        mock_conn = MagicMock()
        mock_pool.getconn.return_value = mock_conn

        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = self.repo.search([0.1] * 1536)
        self.assertIsNone(result)

    @patch("data.pg_repository.get_pool")
    def test_upsert_calls_commit(self, mock_get_pool):
        mock_pool = MagicMock()
        mock_get_pool.return_value = mock_pool

        mock_conn = MagicMock()
        mock_pool.getconn.return_value = mock_conn

        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        self.repo.upsert("test_name", "test_text", [0.1] * 1536)
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_pool.putconn.assert_called_once()


class TestPostgresPlanRepository(unittest.TestCase):
    """Тесты для PostgresPlanRepository."""

    def setUp(self):
        self.repo = PostgresPlanRepository()

    @patch("data.pg_repository.get_pool")
    def test_get_by_id_or_name_returns_plan_data(self, mock_get_pool):
        mock_pool = MagicMock()
        mock_get_pool.return_value = mock_pool

        mock_conn = MagicMock()
        mock_pool.getconn.return_value = mock_conn

        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        # first fetchone for plan, second fetchall for items
        mock_cursor.fetchone.return_value = (1, "testPlan")
        mock_cursor.fetchall.return_value = [("cmd1", '{"key":"val"}')]

        result = self.repo.get_by_id_or_name("testPlan")
        self.assertIsNotNone(result)
        self.assertEqual(result["plan_id"], 1)
        self.assertEqual(len(result["items"]), 1)

    @patch("data.pg_repository.get_pool")
    def test_get_by_id_or_name_returns_none(self, mock_get_pool):
        mock_pool = MagicMock()
        mock_get_pool.return_value = mock_pool

        mock_conn = MagicMock()
        mock_pool.getconn.return_value = mock_conn

        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = self.repo.get_by_id_or_name("nonexistent")
        self.assertIsNone(result)

    @patch("data.pg_repository.get_pool")
    def test_save_calls_commit(self, mock_get_pool):
        mock_pool = MagicMock()
        mock_get_pool.return_value = mock_pool

        mock_conn = MagicMock()
        mock_pool.getconn.return_value = mock_conn

        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (42,)

        from core.command_data import CommandData
        cmd = CommandData.createFromStructuredData("test_cmd", '{"key":"val"}')
        result = self.repo.save("testPlan", [cmd])
        self.assertEqual(result, 42)
        mock_conn.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
