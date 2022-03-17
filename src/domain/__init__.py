from abc import ABC

from sqlalchemy.orm.session import Session


class ABCDomain(ABC):
    model: object

    def __init__(self, session: Session):
        self.session = session


class DomainError(Exception):
    pass
