import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from app.core.database import Base
from datetime import datetime, timezone


class UserStatus(enum.Enum):
    ACTIVE = "A"
    INACTIVE = "I"
    DELETED = "D"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), nullable=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    verification_token = Column(String(128), nullable=True, index=True)
    verification_token_expires = Column(DateTime(timezone=True), nullable=True)
