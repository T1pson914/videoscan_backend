from dotenv import load_dotenv
load_dotenv()


from contextlib import asynccontextmanager
from fastapi import FastAPI
from auth.routes import router as auth_router
from core.db import engine
from core.cache import redis_conn



@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await redis_conn.aclose(close_connection_pool=True)
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)



@app.get('/')
async def main():
    return {'message':'welcome!'}
