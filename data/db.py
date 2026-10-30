import os
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from sqlalchemy.orm import DeclarativeBase



DATABASE_URL = os.getenv('DATABASE_URL')



engine = create_async_engine(
    url=DATABASE_URL
)


session_local = async_sessionmaker(bind=engine,expire_on_commit=False)


async def get_session():
    async with session_local() as session:
        yield session
