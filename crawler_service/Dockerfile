FROM python:3.10 AS crawler_service

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /visible

RUN apt update && apt install -y chromium chromium-driver

COPY ./poetry.lock ./pyproject.toml ./

RUN python -m pip --version
RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel
RUN python -m pip install --no-cache-dir --upgrade poetry==1.1.13

RUN poetry config virtualenvs.create false
RUN poetry install --no-ansi --no-dev --no-interaction

COPY ./manage.py ./manage.py
COPY ./crawler ./crawler

FROM crawler_service AS crawler_service_test

RUN python -m pip install --no-cache-dir --upgrade poetry==1.1.13
RUN poetry install --no-ansi --no-interaction

ENV PYTHONPATH="${PYTHONPATH}:/visible"