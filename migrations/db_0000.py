import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Загружаем переменные из .env
load_dotenv()

host = os.getenv("DB_HOST", "localhost")
port = os.getenv("DB_PORT", "5432")
database = os.getenv("DB_NAME", "knowledge")
username = os.getenv("DB_USERNAME", "postgres")
password = os.getenv("DB_PASSWORD", "postgres")

# Подключаемся к postgres (дефолтная БД) для управления
conn = psycopg2.connect(
    host=host,
    port=port,
    database="postgres",
    user=username,
    password=password
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()

# Удаляем БД, если существует
cursor.execute(
    "SELECT 1 FROM pg_database WHERE datname = %s",
    (database,)
)
if cursor.fetchone():
    print(f"БД '{database}' существует. Удаляем...")
    cursor.execute(f"DROP DATABASE {database}")
    print("БД удалена.")

# Создаём БД заново
print(f"Создаём БД '{database}'...")
cursor.execute(f"CREATE DATABASE {database}")
print("БД создана.")

cursor.close()
conn.close()

# Подключаемся к новой БД
conn = psycopg2.connect(
    host=host,
    port=port,
    database=database,
    user=username,
    password=password
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()

# Активируем расширение pgvector
print("Активируем расширение pgvector...")
cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
print("Расширение pgvector активировано.")

# Создаём таблицу
print("Создаём таблицу knowledge...")
cursor.execute("""
CREATE TABLE knowledge (
    name VARCHAR(512) PRIMARY KEY NOT NULL,
    text TEXT,
    embedding vector(1536)
)
""")

# Создаём полнотекстовый индекс (PostgreSQL GIN)
print("Создаём полнотекстовый индекс...")
cursor.execute("""
CREATE INDEX idx_knowledge_name_fts ON knowledge
USING gin(to_tsvector('english', name))
""")

# Создаём таблицу Plan
print("Создаём таблицу Plan...")
cursor.execute("""
CREATE TABLE "Plan" (
    id SERIAL PRIMARY KEY NOT NULL,
    name VARCHAR(512)
)
""")

# Создаём таблицу PlanItem
print("Создаём таблицу PlanItem...")
cursor.execute("""
CREATE TABLE "PlanItem" (
    id SERIAL PRIMARY KEY NOT NULL,
    number INT,
    plan_id INT REFERENCES "Plan"(id),
    command_name VARCHAR(512),
    command_payload TEXT
)
""")

conn.commit()
cursor.close()
conn.close()
print("Готово!")
