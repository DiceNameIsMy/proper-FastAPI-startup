from abc import ABC

from sqlalchemy.orm.session import Session

from modules.hashid import HashidsClient


class ABCDomain(ABC):
    model: object

    def __init__(self, session: Session, id_hasher: HashidsClient):
        self.session = session
        self.id_hasher = id_hasher


class DomainError(Exception):
    pass
