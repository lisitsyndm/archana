import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, MagicMock
from data.connection import get_connection_params, create_pool, get_pool, close_pool


class TestConnection(unittest.TestCase):
    """Тесты для модуля connection."""

    def tearDown(self):
        # Сбрасываем singleton pool после каждого теста
        import data.connection
        data.connection._pool = None

    @patch("data.connection.os.getenv")
    def test_get_connection_params_returns_dict(self, mock_getenv):
        mock_getenv.return_value = None
        params = get_connection_params()
        self.assertIsInstance(params, dict)
        self.assertIn("host", params)
        self.assertIn("port", params)
        self.assertIn("database", params)
        self.assertIn("user", params)
        self.assertIn("password", params)

    @patch("data.connection.os.getenv")
    def test_get_connection_params_values(self, mock_getenv):
        # Когда env-переменные не заданы, getenv возвращает default
        mock_getenv.side_effect = lambda key, default=None: default
        params = get_connection_params()
        self.assertEqual(params["host"], "localhost")
        self.assertEqual(params["port"], "5432")
        self.assertEqual(params["database"], "knowledge")
        self.assertEqual(params["user"], "postgres")
        self.assertEqual(params["password"], "postgres")

    @patch("data.connection.ThreadedConnectionPool")
    def test_create_pool_returns_pool(self, MockPool):
        mock_pool_instance = MagicMock()
        MockPool.return_value = mock_pool_instance
        result = create_pool()
        MockPool.assert_called_once()
        self.assertEqual(result, mock_pool_instance)

    @patch("data.connection.create_pool")
    def test_get_pool_lazy_init(self, mock_create_pool):
        mock_create_pool.return_value = MagicMock()
        import data.connection
        data.connection._pool = None
        result = get_pool()
        mock_create_pool.assert_called_once()

    @patch("data.connection.ThreadedConnectionPool")
    def test_close_pool(self, MockPool):
        mock_pool_instance = MagicMock()
        MockPool.return_value = mock_pool_instance
        import data.connection
        data.connection._pool = mock_pool_instance
        close_pool()
        mock_pool_instance.closeall.assert_called_once()
        self.assertIsNone(data.connection._pool)


if __name__ == "__main__":
    unittest.main()
