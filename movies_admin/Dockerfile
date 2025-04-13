FROM python:3.10

WORKDIR /opt/app

ENV DJANGO_SETTINGS_MODULE='config.settings'

COPY requirements.txt requirements.txt
COPY uwsgi/uwsgi.ini uwsgi.ini

RUN  pip install --upgrade pip --no-cache-dir && \
     pip install -r requirements.txt --no-cache-dir

COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]