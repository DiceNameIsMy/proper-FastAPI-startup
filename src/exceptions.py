from typing import Any, Optional
from fastapi import HTTPException, status


invalid_credentials = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="invalid-credentials",
)


class BadRequest(HTTPException):
    def __init__(
        self,
        detail: Any = None,
        headers: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, headers)


class BadCredentials(HTTPException):
    def __init__(
        self,
        detail: Any = "Could not validate credentials",
        headers: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, headers)


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
