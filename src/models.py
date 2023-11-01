from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class AppRequest(Base):
    __tablename__ = "AppRequest"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    link: Mapped[str]
    is_done: Mapped[bool]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())

    def __str__(self):
        return f"{self.__class__.__name__}(link={self.link}, is_done={self.is_done})"

    def __repr__(self):
        return str(self)
