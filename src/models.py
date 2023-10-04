import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, Text

from .database import Base


class AppRequest(Base):
    __tablename__ = "AppRequest"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    link = Column(Text)
    is_done = Column(Boolean)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
