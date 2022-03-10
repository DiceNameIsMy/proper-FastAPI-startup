from domain import DomainError


class UserDomainError(DomainError):
    pass


class UserAlreadyExistError(UserDomainError):
    pass


class UserNotFoundError(UserDomainError):
    pass
