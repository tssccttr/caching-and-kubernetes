# base arguments to leverage across build stages
ARG APP_DIR=/app
ARG PYTHON_VERSION=3.11
ARG POETRY_VERSION=1.8.2

# Build Image
FROM python:${PYTHON_VERSION}-slim AS build
ARG APP_DIR
ARG POETRY_VERSION

RUN apt-get update && apt-get install -y \
  curl build-essential libffi-dev \
  && rm -rf /var/lib/apt/lists/*

# install poetry and add to path
RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH /root/.local/bin:$PATH

# change work directory for where app will live
WORKDIR ${APP_DIR}
COPY pyproject.toml poetry.lock ./

# copy over the venv including any symbolic links
RUN python -m venv --copies ${APP_DIR}/venv
RUN . ${APP_DIR}/venv/bin/activate && poetry install --no-root --only main

# Deployment image
FROM python:${PYTHON_VERSION}-slim as lab3
ARG APP_DIR

COPY --from=build ${APP_DIR}/venv ${APP_DIR}/venv/
ENV PATH ${APP_DIR}/venv/bin:$PATH

WORKDIR ${APP_DIR}/
COPY . ./

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0"]
