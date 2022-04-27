from abc import ABC

from sqlalchemy.orm.session import Session

from utils.hashing import IDHasher


class ABCDomain(ABC):
    model: object

    def __init__(self, session: Session, id_hasher: IDHasher):
        self.session = session
        self.id_hasher = id_hasher


class DomainError(Exception):
    pass
