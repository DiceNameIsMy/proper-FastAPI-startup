FROM python:3.10.4-slim

# install initial dependencies
RUN pip install --no-cache-dir --upgrade pip pipenv

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1
ENV APP_HOME=/app/

WORKDIR ${APP_HOME}

# install dependencies
COPY Pipfile.lock Pipfile ${APP_HOME}
RUN pipenv install --system
