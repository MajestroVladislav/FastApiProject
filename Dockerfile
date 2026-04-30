FROM python:3.10-alpine

ENV PATH="${PATH}:/root/.local/bin"

WORKDIR /application

COPY ./app /application/app
COPY ./alembic /application/alembic
COPY ./exeptions /application/exeptions
COPY ./alembic.ini /application/alembic.ini
COPY ./requirements.txt /application/requirements.txt
COPY ./start.sh /application/start.sh
COPY ./main.py /application/main.py

ENV PYTHONPATH=/application/app

RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev

RUN pip install --no-cache-dir -r /application/requirements.txt

RUN chmod +x /application/start.sh

RUN ls -l /application/start.sh
RUN ls -l /application/main.py

EXPOSE 8000

