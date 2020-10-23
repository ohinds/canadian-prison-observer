FROM python:3.8

ENV FLASK_APP run.py

COPY run.py gunicorn-cfg.py Pipfile ./
COPY app app

RUN pip install --upgrade pipenv
RUN pipenv install

EXPOSE 8080
CMD ["pipenv", "run", "gunicorn", "--config", "gunicorn-cfg.py", "run:app"]
