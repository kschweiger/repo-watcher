# syntax=docker/dockerfile:1

FROM python:3.9.12-slim-bullseye

RUN apt-get update && apt-get install -y git

WORKDIR /app

COPY requirements/prod.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install -e .

CMD [ "run-watcher", "tag", "--repo",  "/repo", "--pattern",  "*", "--log_level", "DEBUG"]