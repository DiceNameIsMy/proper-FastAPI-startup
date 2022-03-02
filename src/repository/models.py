from sqlalchemy import String, Column, Integer, Boolean

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(127), unique=True)
    password = Column(String(255))
    is_active = Column(Boolean(), default=True)
