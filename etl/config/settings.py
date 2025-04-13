from pydantic import Field, AnyUrl
from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    # PostgreSQL настройки
    db_name: str = Field(..., env="DB_NAME")
    db_user: str = Field(..., env="DB_USER")
    db_password: str = Field(..., env="DB_PASSWORD")
    db_host: str = Field(..., env="DB_HOST")
    db_port: str = Field(..., env="DB_PORT")

    @property
    def postgres_dsl(self) -> dict:
        """Возвращает параметры для psycopg в вашем формате"""
        return {
            'dbname': self.db_name,
            'user': self.db_user,
            'password': self.db_password,
            'host': self.db_host,
            'port': self.db_port
        }

    # Elasticsearch настройки
    elastic_host: str = Field(..., env="ELASTIC_HOST")
    elastic_port: int = Field(..., env="ELASTIC_PORT")
    elastic_scheme: str = Field(..., env="ELASTIC_SCHEME")

    @property
    def elastic_dsn(self) -> AnyUrl:
        return f"{self.elastic_scheme}://{self.elastic_host}:{self.elastic_port}"

    # Общие настройки
    elastic_index: str = Field(..., env="ELASTIC_INDEX")
    state_file_path: str = Field(..., env="STATE_FILE_PATH")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Settings()
