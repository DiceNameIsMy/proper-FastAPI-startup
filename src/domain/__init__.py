from abc import ABC

from sqlalchemy.orm.session import Session

from modules.hashid import HashidsClient
from modules.pwd import PwdClient


class ABCDomain(ABC):
    model: object

    def __init__(self, session: Session, id_hasher: HashidsClient, pwd_client: PwdClient):
        self.session = session
        self.id_hasher = id_hasher
        self.pwd_client = pwd_client


class DomainError(Exception):
    pass
