from sqlalchemy import Column, Integer, String, Enum
from app.core.database import Base
import enum

class StatusEnum(str, enum.Enum):
    ACTIVE = "A"
    INACTIVE = "I"
    DELETED = "D"

class URLBucket(Base):
    __tablename__ = "url_bucket"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String(500), nullable=False)
    short_url = Column(String(100), unique=True, index=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.ACTIVE)
