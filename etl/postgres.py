import logging
import os
from contextlib import contextmanager
from datetime import datetime

import psycopg
from psycopg import connect, ClientCursor, OperationalError
from psycopg.rows import dict_row

from backoff_self.backoff import backoff


class PostgresConnector:
    """Подключение к PostgreSQL"""

    def __init__(self):
        self.dsl =  {'dbname': os.getenv('DB_NAME'),
                     'user': os.getenv('DB_USER'),
                     'password': os.getenv('DB_PASSWORD'),
                     'host': os.getenv('DB_HOST'),
                     'port': os.getenv('DB_PORT')
                     }
        self.logger = logging.getLogger(__name__)

    @backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10, jitter=True)
    def _create_connection(self):
        """Функция подключения с повторными попытками"""
        return connect(**self.dsl, row_factory=dict_row, cursor_factory=ClientCursor)

    @contextmanager
    def connect(self):
        """Контекстный менеджер для подключения к PostgreSQL."""
        conn = None
        try:
            conn = self._create_connection()
            self.logger.info("Соединение с PostgreSQL установлено.")
            yield conn
        except OperationalError:
            self.logger.exception("Ошибка при подключении к PostgreSQL")
            raise
        finally:
            if conn:
                conn.close()
                self.logger.info("Соединение с PostgreSQL закрыто")


def get_modified(cursor, state, query, table_name: str) -> tuple[list, bool]:
    modified = state.get_state(f"temporary_{table_name}")
    if modified is None:
        modified = "-infinity"
    else:
        modified = datetime.fromisoformat(modified)

    try:
        result = cursor.execute(query, (modified,)).fetchall()
        return result, False
    except psycopg.Error:
        logging.exception(f"Ошибка при получении пачки изменений в таблице {table_name}")
        return [], True


def get_film_works_by_persons_or_genres_modified(cursor, state, query: str, data: list, table_name: str) -> tuple[list, bool]:
    modified = state.get_state(f"temporary_film_works_by_{table_name}")
    if modified != "-infinity":
        modified = datetime.fromisoformat(modified)

    try:
        return cursor.execute(query, (*data, modified)).fetchall(), False
    except psycopg.Error:
        logging.exception(f"Ошибка при получении id фильмов по id измененных в {table_name}")
        return [], True


def get_results(cursor, query, data, table_name: str):
    try:
        return cursor.execute(query, data).fetchall(), False
    except psycopg.Error:
        logging.exception(f"Ошибка при получении данных из-за изменений в {table_name}")
        return [], True
