# Outdated!
Currently I do not consider this template as a good one. New revision will be made sometime in the future

# proper-FastAPI-startup

My vision of pretty good FastAPI project template to start with. It features -
- Registration, Sending code to email to verify it, Authentication
- OAuth2 authorization with JWT tokens
- OAuth2 with google provider
- Idempotent requests for POST and PATCH methods
- HashIds to keep your ID's somewhat secure
- Simple API to view users
- Pipenv as dependency control tool
- SqlAlchemy and Alembic to speak with DB and manage migrations
- Some conceps from Domain Driven Design
- Sentry integration
- black, flake8 and mypy code checkers
- pytest for testing
- Docker and docker-compose builder


## Setup

To run API use these commands

    cp compose/local/.env-sample compose/local/.env  # use sample .env file for local build
    openssl genrsa -out jwtRSA256-private.pem 2048  # generate private jwt key for RD265 algorithm
    openssl rsa -in jwtRSA256-private.pem -pubout -outform PEM -out jwtRSA256-public.pem  # generate public jwt key for RD265 algorithm
    pipenv run local up --build  # build and run api

To setup development environment also use these

    pipenv install --dev
    pipenv run pre-commit install

Useful commands

    pipenv run test  # run api tests
    pipenv run lint  # run flake8 and mypy
    pipenv run makemigrations  # create database migration
    pipenv run down  # shut down all containers
