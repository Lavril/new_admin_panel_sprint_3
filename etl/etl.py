import logging
import time

from dotenv import load_dotenv

from elastic import ElasticConnector
from extractor import Extractor
from loader import ElasticsearchLoader, generate_actions
from models.models import FilmWork


def run_etl():
    es_connector = ElasticConnector()
    es_connector.create_index_if_not_exists()
    loader = ElasticsearchLoader(es_connector)
    while True:
        start_etl_time = time.time()
        extractor = Extractor()
        for table_name in ['person', 'genre']:
            for extracted_data in extractor.extract_persons_or_genres(table_name):
                transformed_data = transformation(extracted_data)
                actions = generate_actions(transformed_data, "movies")
                success = loader.bulk_load(actions, "movies")
                if not success:
                    raise Exception("Ошибка при загрузке данных в Elasticsearch")

        for extracted_data in extractor.extract_film_works():
            transformed_data = transformation(extracted_data)
            actions = generate_actions(transformed_data, "movies")
            success = loader.bulk_load(actions, "movies")
            if not success:
                raise Exception("Ошибка при загрузке данных в Elasticsearch")
        time.sleep(15 * 60 - (time.time() - start_etl_time))


def transformation(film_works: dict[str, FilmWork]) -> list[dict]:
    """Преобразование данных перед загрузкой в Elasticsearch."""
    return [{
        "id": film.id,
        "imdb_rating": film.imdb_rating,
        "genres": [genre.name for genre in film.genres],
        "title": film.title,
        "description": film.description,
        "directors_names": film.directors_names,
        "actors_names": film.actors_names,
        "writers_names": film.writers_names,
        "directors": [{"id": d.id, "name": d.name} for d in film.directors],
        "actors": [{"id": a.id, "name": a.name} for a in film.actors],
        "writers": [{"id": w.id, "name": w.name} for w in film.writers],
    } for film in film_works.values()]


if __name__ == '__main__':
    load_dotenv()
    logging.basicConfig(level=logging.INFO, filename="logs/etl.log", filemode="w",
                        format="%(asctime)s %(name)s %(levelname)s %(message)s")

    run_etl()
