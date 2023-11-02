from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeMeta, declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from config import settings


URL = (
    f"postgresql+asyncpg://"
    f"{settings.db.user}:{settings.db.password}"
    f"@{settings.db.host}:{settings.db.port}"
    f"/{settings.db.name}"
)

Base: DeclarativeMeta = declarative_base()

engine = create_async_engine(URL, poolclass=NullPool)
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
        await session.close()
