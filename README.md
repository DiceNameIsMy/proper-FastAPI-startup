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
