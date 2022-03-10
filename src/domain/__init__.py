from abc import ABC

from sqlalchemy.orm.session import Session


class ABCDomain(ABC):
    model: object

    def __init__(self, session: Session):
        self.session = session

    @classmethod
    def parse_filter_kwargs(cls, filters: dict) -> list:
        return [
            getattr(cls.model, field) == value for field, value in enumerate(filters)
        ]


class DomainError(Exception):
    pass
