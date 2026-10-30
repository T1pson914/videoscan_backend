import os
import jwt
from datetime import datetime,timedelta,timezone
from uuid import uuid4,UUID
from auth.models import RefreshToken
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from fastapi import HTTPException



ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
REFRESH_TOKEN_EXPIRE_DAYS = os.getenv('REFRESH_TOKEN_EXPIRE_DAYS')
JWT_ALGROTITHM = os.getenv('JWT_ALGROTITHM')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')



def create_token(user_id: int, token_type: str) -> tuple[str,dict]:

    exp = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    if token_type=='refresh':
        exp = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        'sub':str(user_id),
        'jti':uuid4(),
        'exp':exp,
        'token_type':token_type
    }

    return jwt.encode(payload,JWT_SECRET_KEY,JWT_ALGROTITHM),payload



def create_access_token(user_id: int) -> str:
    access_token,_ = create_token(user_id,'access')
    return access_token



async def create_refresh_token(user_id: int, session: AsyncSession) -> str:
    refresh_token,payload = create_token(user_id,'refresh')
    user_id = int(payload.get('sub'))
    jti = UUID(payload.get('jti'))
    expired_at = payload.get('exp')
    stored = RefreshToken(
        jti=jti,
        user_id=user_id,
        expired_at=expired_at
    )
    session.add(stored)
    await session.commit()
    return refresh_token



async def create_token_pair(user_id: int, session: AsyncSession) -> dict[str,str]:
    access_token = create_access_token(user_id)
    refresh_token = await create_refresh_token(user_id,session)
    return {'access_token':access_token,'refresh_token':refresh_token}



def decode_access_token(access_token: str) -> dict:
    credentials_error = HTTPException(status_code=400,detail='Couldnt validate access token.')
    try:
        payload = jwt.decode(access_token,JWT_ALGROTITHM,algorithms=[JWT_ALGROTITHM])
        jti = payload.get('jti')
        sub = payload.get('sub')
        token_type = payload.get('token_type')
        if not jti or not sub or token_type!='access':
            raise credentials_error
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401,detail='Access token expired.')
    except jwt.PyJWTError:
        raise credentials_error
    return payload



async def decode_refresh_token(refresh_token: str, session: AsyncSession) -> dict:
    credentials_error = HTTPException(status_code=400,detail='Couldnt validate refresh token.')
    try:
        payload = jwt.decode(refresh_token,JWT_ALGROTITHM,algorithms=[JWT_ALGROTITHM])
        jti = UUID(payload.get('jti'))
        sub = payload.get('sub')
        token_type = payload.get('token_type')
        if not jti or not sub or token_type!='refresh':
            raise credentials_error
    except jwt.ExpiredSignatureError:
        await session.execute(delete(RefreshToken).where(jti=jti))
        await session.commit()
        raise HTTPException(status_code=401,detail='Refresh token expired.')
    except jwt.PyJWTError:
        raise credentials_error
    return payload
