from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base
from datetime import datetime, timezone

class Record(Base):
    __tablename__ = "transaction_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    trans_id = Column(Integer, nullable=True)       # FIXED
    user_id = Column(Integer, nullable=True)
    device_id = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    ip_address = Column(String(50), nullable=True)
