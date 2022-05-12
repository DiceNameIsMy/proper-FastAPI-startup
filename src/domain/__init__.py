from abc import ABC

from modules.hashid import HashidsClient
from modules.pwd import PwdClient


class ABCDomain(ABC):
    model: object

    def __init__(self, id_hasher: HashidsClient, pwd_client: PwdClient):
        self.id_hasher = id_hasher
        self.pwd_client = pwd_client


class DomainError(Exception):
    pass
