from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Person(BaseModel):
    id: str
    name: str


class Genre(BaseModel):
    id: str
    name: str


class FilmWork(BaseModel):
    id: str
    title: str
    description: Optional[str]
    imdb_rating: Optional[float]
    creation_date: Optional[datetime]
    type: str
    genres: List[Genre]
    directors: List[Person]
    actors: List[Person]
    writers: List[Person]
    directors_names: List[str]
    actors_names: List[str]
    writers_names: List[str]
    updated_at: Optional[datetime]
