FROM python:3.10-alpine3.15 as base

ARG TG_TOKEN

ENV TG_TOKEN=${TG_TOKEN} \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.1.12

RUN apk add --no-cache gcc musl-dev libffi-dev
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app
COPY poetry.lock pyproject.toml /app/

RUN POETRY_VIRTUALENVS_CREATE=false \
    poetry install --no-dev --no-interaction --no-ansi

COPY . /app

CMD ["python", "./src/bot.py"]