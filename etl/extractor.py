import logging
import os

from models.models import FilmWork, Person, Genre
from postgres import PostgresConnector, get_results, \
    get_film_works_by_persons_or_genres_modified, get_modified
from state import JsonFileStorage, State


class Extractor:
    """Извлечение данных из PostgreSQL"""

    def __init__(self):
        storage = JsonFileStorage(os.getenv('STORAGE'))

        self.state = State(storage)
        self.logger = logging.getLogger(__name__)
        self.pg_connector = PostgresConnector()

        self.select_data_by_modified = """
                SELECT
                    fw.id as fw_id, 
                    fw.title, 
                    fw.description, 
                    fw.rating, 
                    fw.type, 
                    fw.created, 
                    fw.modified, 
                    pfw.role, 
                    p.id, 
                    p.full_name,
                    g.id as g_id,
                    g.name
                FROM content.film_work fw
                LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
                LEFT JOIN content.person p ON p.id = pfw.person_id
                LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
                LEFT JOIN content.genre g ON g.id = gfw.genre_id
                WHERE fw.id IN ({0});
                """

    def extract_persons_or_genres(self, table_name: str):
        """Извлечение новых данных из таблицы person или genre"""
        select_modified = get_select_modified(table_name)

        select_film_works_by_modified = f"""
            SELECT fw.id, fw.modified
            FROM content.film_work fw
            LEFT JOIN content.{table_name}_film_work tfw ON tfw.film_work_id = fw.id
            WHERE tfw.{table_name}_id IN ({{0}}) AND fw.modified > %s
            ORDER BY fw.modified
            LIMIT 100;
            """

        with self.pg_connector.connect() as pg_conn:
            with pg_conn.cursor() as cursor:
                modified = self.state.get_state(table_name)
                self.state.set_state(f'temporary_{table_name}', modified)

                while True:
                    data, err = get_modified(cursor, self.state, select_modified, table_name)
                    if err:
                        # TODO обработать ошибку
                        return

                    if not data:
                        break

                    last_modified = data[-1]['modified'].isoformat()
                    self.state.set_state(f'temporary_{table_name}', last_modified)
                    logging.info(f"Взяли результаты из {table_name} по {last_modified}")

                    part_ids = [str(db_part["id"]) for db_part in data]

                    temporary_select = select_film_works_by_modified.format(",".join(["%s"] * len(part_ids)))
                    self.state.set_state(f'temporary_film_works_by_{table_name}', "-infinity")
                    while True:
                        data, err = get_film_works_by_persons_or_genres_modified(cursor, self.state, temporary_select, part_ids, table_name)
                        if err:
                            # TODO обработать ошибку
                            return
                        if not data:
                            break

                        # print("film_works_by_persons:", data)

                        last_modified = data[-1]['modified'].isoformat()
                        self.state.set_state(f'temporary_film_works_by_{table_name}', last_modified)

                        yield get_film_data(cursor, self.select_data_by_modified, data, table_name)

                    self.state.set_state(table_name, self.state.get_state(f"temporary_{table_name}"))

    def extract_film_works(self, table_name: str = 'film_work'):
        """Извлечение новых данных из таблицы person или genre"""
        select_modified = get_select_modified(table_name)

        with self.pg_connector.connect() as pg_conn:
            with pg_conn.cursor() as cursor:
                modified = self.state.get_state(table_name)
                self.state.set_state(f'temporary_{table_name}', modified)

                while True:
                    data, err = get_modified(cursor, self.state, select_modified, table_name)
                    if err:
                        # TODO обработать ошибку
                        return

                    if not data:
                        break

                    last_modified = data[-1]['modified'].isoformat()
                    self.state.set_state(f'temporary_{table_name}', last_modified)
                    logging.info(f"Взяли результаты из {table_name} по {last_modified}")

                    yield get_film_data(cursor, self.select_data_by_modified, data, table_name)

                    self.state.set_state(table_name, self.state.get_state(f"temporary_{table_name}"))


def get_select_modified(table_name: str) -> str:
    """
    Запрос для получения изменённых записей в указанной таблице.

    :param table_name: Название таблицы
    :return: SQL запрос
    """
    return f"""
            SELECT id, modified
            FROM content.{table_name}
            WHERE modified > %s
            ORDER BY modified
            LIMIT 100;
            """


def get_film_data(cursor, query: str, data: list, table_name: str) -> dict[str, FilmWork]:
    """Функция для получения информации по фильмам"""
    film_works_ids = [str(db_part["id"]) for db_part in data]
    temporary_select = query.format(",".join(["%s"] * len(film_works_ids)))
    data, err = get_results(cursor, temporary_select, film_works_ids, table_name)
    if err:
        # TODO обработать ошибку
        raise Exception("Ошибка при получении данных из БД")

    # Собираем данные для будущего transform
    to_transform = {}
    for film_work in data:
        film_work_id = str(film_work["fw_id"])
        current_role = film_work["role"]
        if film_work["full_name"]:
            to_write_role = Person(id=str(film_work["id"]),
                                   name=film_work["full_name"]
                                   )
        to_write_genre = Genre(id=str(film_work["g_id"]),
                               name=film_work["name"]
                               )
        if film_work_id in to_transform:
            for genre in to_transform[film_work_id].genres:
                if genre.name == film_work["name"]:
                    break
            else:
                to_transform[film_work_id].genres.append(to_write_genre)

            if film_work["full_name"] and current_role == 'writer' and film_work["full_name"] not in to_transform[
                film_work_id].writers_names:
                to_transform[film_work_id].writers.append(to_write_role)
                to_transform[film_work_id].writers_names.append(film_work["full_name"])
            elif film_work["full_name"] and current_role == 'actor' and film_work["full_name"] not in to_transform[
                film_work_id].actors_names:
                to_transform[film_work_id].actors.append(to_write_role)
                to_transform[film_work_id].actors_names.append(film_work["full_name"])
            elif film_work["full_name"] and current_role == 'director' and film_work["full_name"] not in to_transform[
                film_work_id].directors_names:
                to_transform[film_work_id].directors.append(to_write_role)
                to_transform[film_work_id].directors_names.append(film_work["full_name"])
        else:
            role = {"director": [], "actor": [], "writer": []}
            role[current_role] = [to_write_role]

            role_names = {"director": [], "actor": [], "writer": []}
            role_names[current_role] = [film_work["full_name"]]

            to_transform[film_work_id] = FilmWork(
                id=film_work_id,
                title=film_work["title"],
                description=film_work["description"],
                imdb_rating=film_work["rating"],
                creation_date=film_work["created"],
                type=film_work["type"],
                genres=[to_write_genre],
                directors=role["director"],
                actors=role["actor"],
                writers=role["writer"],
                directors_names=role_names["director"],
                actors_names=role_names["director"],
                writers_names=role_names["director"],
                updated_at=film_work["modified"]
            )
    return to_transform
