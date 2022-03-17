from datetime import datetime

from sqlalchemy import (
    String,
    Column,
    Integer,
    DateTime,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from pydantic import EmailStr

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True)
    email: EmailStr = Column(String(127), unique=True, nullable=False)
    password: str = Column(String(255), nullable=False)
    is_active: bool = Column(Boolean(), default=True, nullable=False)
    is_email_verified: bool = Column(Boolean(), default=False, nullable=False)

    verification_codes: list["VerificationCode"] = relationship(
        "VerificationCode", back_populates="user"
    )


class VerificationCode(Base):
    __tablename__ = "verification_codes"
    __table_args__ = (
        UniqueConstraint("user_id", "code"),
        Index("verification_codes_user_id_idx", "user_id", "code"),
    )

    id: int = Column(Integer, primary_key=True)
    code: int = Column(Integer, nullable=False)
    user_id: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    expires_at: datetime = Column(DateTime(timezone=True), nullable=False)

    user: User = relationship("User", back_populates="verification_codes")
