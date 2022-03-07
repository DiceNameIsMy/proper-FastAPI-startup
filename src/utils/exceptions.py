from typing import Any, Optional
from fastapi import HTTPException, status


bad_credentials = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
invalid_credentials = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="invalid-credentials",
)


class NotFound(HTTPException):
    def __init__(
        self, detail: Any = None, headers: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail, headers)


class PermissionDenied(HTTPException):
    def __init__(
        self, detail: Any = None, headers: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, detail, headers)
