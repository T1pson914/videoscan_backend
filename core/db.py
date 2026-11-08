import os
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from typing import AsyncGenerator



DATABASE_URL = os.getenv('DATABASE_URL')



engine = create_async_engine(
    url=DATABASE_URL
)


session_local = async_sessionmaker(bind=engine,expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession,None]:
    async with session_local() as session:
        yield session
