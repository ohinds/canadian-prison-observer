FROM python:latest

WORKDIR /app

RUN pip install --upgrade pip && \
    pip install --no-cache-dir pipenv

ADD Pipfile /app/

RUN pipenv install

ADD . /app/

EXPOSE 80
CMD pipenv run gunicorn -c gunicorn.conf.py --log-file=- -b 0.0.0.0:80 app:app
