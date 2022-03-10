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

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(127), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean(), default=True, nullable=False)
    is_email_verified = Column(Boolean(), default=False, nullable=False)

    verification_codes = relationship("VerificationCode", back_populates="user")


class VerificationCode(Base):
    __tablename__ = "verification_codes"
    __table_args__ = (
        UniqueConstraint("user_id", "code"),
        Index("verification_codes_user_id_idx", "user_id", "code"),
    )

    id = Column(Integer, primary_key=True)
    code = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User", back_populates="verification_codes")
