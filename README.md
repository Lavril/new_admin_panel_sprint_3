## Подготовка к запуску
1. Заполните данные в .env для создания суперпользователя и подключения к БД

## Запуск
 ```docker compose up --build``` - запуск контейнера

## Что сделано по заданиям
1. Добавлен сбор статики, создание суперпользователя, миграции.
2. Настроен полный запуск через docker compose.
3. Убрана версия nginx из заголовков.
4. Прописан location /admin
5. Настроена статика в nginx

## Задание:Elasticsearch
1. Тесты проходят.
2. Написани docker-compose

## Postman
Дл тестирования nginx нужно использовать следующий файл:
new_admin_panel_sprint_1/movies_admin/postman/movies API.postman_collection.json.
В нём поле genres поменяно на genres_list.




Описание структуры и порядок выполнения проекта:
1. `schema_design` - раздел с материалами для архитектуры базы данных.
2. `movies_admin` - раздел с материалами для панели администратора.
3. `sqlite_to_postgres` - раздел с материалами по миграции данных.




## Готовность
Всё сделано в соответствии с заданием. Для третьего задания написан более подробный README.

### Запуск postgres
```
docker run -d \
  --name NAME \
  -p PORT:PORT \
  -v $HOME/postgresql/data:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=PASSWORD \
  -e POSTGRES_USER=NAME \
  -e POSTGRES_DB=NAME  \
  postgres:16
```
  
### Команды postgres
```docker ps``` - запущенный контейнеры
```docker ps -a``` - все контейнеры
```psql -h 127.0.0.1 -U app -d movies_database``` - подключиться к любому доступному в вашей сети серверу PostgreSQL
```docker exec -it movies-postgres bash``` - вход в контейнер

### Запуски
```docker run -p 8080:8080 --name swagger -v ./swagger/openapi.yaml:/swagger.yaml -e SWAGGER_JSON=/swagger.yaml swaggerapi/swagger-ui``` - swagger
```docker compose up --build``` - запуск контейнера





