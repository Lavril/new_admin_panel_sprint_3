import logging
from contextlib import contextmanager

from elasticsearch import Elasticsearch

from backoff_self.backoff import backoff
from config.settings import settings


class ElasticConnector:
    """Подключение к Elasticsearch."""

    def __init__(self):
        self.index = settings.elastic_index
        self.client = None
        self.dsn = settings.elastic_dsn
        self.logger = logging.getLogger(__name__)

    @backoff(start_sleep_time=1, factor=2, border_sleep_time=30, max_retries=10, jitter=True)
    def _connect(self):
        """Метод для подключения с backoff."""
        self.client = Elasticsearch(
            hosts=[self.dsn],
            max_retries=5,
            retry_on_timeout=True,
            retry_on_status=(502, 503, 504, 429)
        )
        if not self.client.ping():
            raise ConnectionError("Elasticsearch не доступен")
        return self.client

    @contextmanager
    def connect(self):
        """Контекстный менеджер для подключения к Elasticsearch."""
        try:
            self._connect()
            self.logger.info("Подключение с Elasticsearch установлено")
            yield self.client
        except Exception:
            self.logger.exception("Ошибка в Elasticsearch")
            raise
        finally:
            if self.client:
                self.client.close()
                self.logger.info("Соединение с Elasticsearch закрыто")

    def create_index_if_not_exists(self) -> None:
        """Создать индекс если он не существует."""
        with self.connect() as client:
            try:
                if not client.indices.exists(index=self.index):
                    client.indices.create(
                        index=self.index,
                        body={
                              "settings": {
                                "refresh_interval": "1s",
                                "analysis": {
                                  "filter": {
                                    "english_stop": {
                                      "type":       "stop",
                                      "stopwords":  "_english_"
                                    },
                                    "english_stemmer": {
                                      "type": "stemmer",
                                      "language": "english"
                                    },
                                    "english_possessive_stemmer": {
                                      "type": "stemmer",
                                      "language": "possessive_english"
                                    },
                                    "russian_stop": {
                                      "type":       "stop",
                                      "stopwords":  "_russian_"
                                    },
                                    "russian_stemmer": {
                                      "type": "stemmer",
                                      "language": "russian"
                                    }
                                  },
                                  "analyzer": {
                                    "ru_en": {
                                      "tokenizer": "standard",
                                      "filter": [
                                        "lowercase",
                                        "english_stop",
                                        "english_stemmer",
                                        "english_possessive_stemmer",
                                        "russian_stop",
                                        "russian_stemmer"
                                      ]
                                    }
                                  }
                                }
                              },
                              "mappings": {
                                "dynamic": "strict",
                                "properties": {
                                  "id": {
                                    "type": "keyword"
                                  },
                                  "imdb_rating": {
                                    "type": "float"
                                  },
                                  "genres": {
                                    "type": "keyword"
                                  },
                                  "title": {
                                    "type": "text",
                                    "analyzer": "ru_en",
                                    "fields": {
                                      "raw": {
                                        "type":  "keyword"
                                      }
                                    }
                                  },
                                  "description": {
                                    "type": "text",
                                    "analyzer": "ru_en"
                                  },
                                  "directors_names": {
                                    "type": "text",
                                    "analyzer": "ru_en"
                                  },
                                  "actors_names": {
                                    "type": "text",
                                    "analyzer": "ru_en"
                                  },
                                  "writers_names": {
                                    "type": "text",
                                    "analyzer": "ru_en"
                                  },
                                  "directors": {
                                    "type": "nested",
                                    "dynamic": "strict",
                                    "properties": {
                                      "id": {
                                        "type": "keyword"
                                      },
                                      "name": {
                                        "type": "text",
                                        "analyzer": "ru_en"
                                      }
                                    }
                                  },
                                  "actors": {
                                    "type": "nested",
                                    "dynamic": "strict",
                                    "properties": {
                                      "id": {
                                        "type": "keyword"
                                      },
                                      "name": {
                                        "type": "text",
                                        "analyzer": "ru_en"
                                      }
                                    }
                                  },
                                  "writers": {
                                    "type": "nested",
                                    "dynamic": "strict",
                                    "properties": {
                                      "id": {
                                        "type": "keyword"
                                      },
                                      "name": {
                                        "type": "text",
                                        "analyzer": "ru_en"
                                      }
                                    }
                                  }
                                }
                              }
                        })
                    self.logger.info(f"Created index {self.index}")
            except Exception:
                self.logger.exception("Failed to create index")
                raise
