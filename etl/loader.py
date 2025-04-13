import logging

from elasticsearch import helpers
from typing import Iterator

from backoff_self.backoff import backoff


class ElasticsearchLoader:
    def __init__(self, es_connector):
        self.es = es_connector
        self.logger = logging.getLogger(__name__)

    @backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10, max_retries=10, jitter=True)
    def bulk_load(self, actions: Iterator[dict], index: str) -> bool:
        """
        Массовая загрузка данных в Elasticsearch с обработкой ошибок

        :param actions: Итератор действий для bulk-запроса
        :param index: Название индекса
        :return: Статус выполнения (True - успех, False - есть ошибки)
        """
        try:
            with self.es.connect() as es_client:
                for ok, item in helpers.streaming_bulk(
                        es_client,
                        actions,
                        index=index,
                        raise_on_error=False,
                        max_retries=2,
                        initial_backoff=1,
                        chunk_size=500,
                        refresh=True
                ):
                    if not ok:
                        self.logger.error(f"Добавление прервано. Не внесён элемент: {item}")

            return True
        except Exception:
            self.logger.exception("Ошибка при bulk-загрузке")
            return False


def generate_actions(film_data: list[dict], index: str) -> Iterator[dict]:
    """
    Генератор действий для bulk-запроса

    :param index: Название индекса
    :param film_data: Список словарей с данными фильмов
    :yield: Действия для Elasticsearch в формате bulk API
    """
    for film in film_data:
        yield {
            "_op_type": "index",  # или "update" для обновления
            "_index": index,
            "_id": film["id"],
            "_source": film
        }
