FROM python:3.8

ENV FLASK_APP run.py

COPY run.py gunicorn-cfg.py Pipfile ./

RUN pip install --upgrade pipenv
RUN pipenv install

COPY app app

EXPOSE 8080
CMD ["pipenv", "run", "gunicorn", "--config", "gunicorn-cfg.py", "run:app"]
