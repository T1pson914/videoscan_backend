import os
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from typing import AsyncGenerator
from config import settings



engine = create_async_engine(
    url=settings.database_url
)


session_local = async_sessionmaker(bind=engine,expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession,None]:
    async with session_local() as session:
        yield session
