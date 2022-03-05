from sqlalchemy.orm.session import Session

from repository.database import SessionLocal


def get_db_session() -> Session:
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
