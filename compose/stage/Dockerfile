FROM python:3.10.4-slim

# install initial dependencies
RUN pip install --no-cache --upgrade pip pipenv

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1
ENV APP_HOME=/app

WORKDIR ${APP_HOME}

# create the app user & permit to use app files
RUN addgroup appgroup && useradd -g appgroup appuser && \
    chown -R appuser:appgroup $APP_HOME

# install dependencies
COPY Pipfile.lock Pipfile ${APP_HOME}/
RUN pipenv install --system

COPY src ${APP_HOME}/src

# change to the app user
USER appuser
