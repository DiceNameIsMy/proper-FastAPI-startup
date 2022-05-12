from abc import ABC

from sqlalchemy.orm import Session


class ABCReposotory(ABC):
    def __init__(self, session: Session) -> None:
        self.session = session
