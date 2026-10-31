from typing import Annotated
from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException,Body,Request,Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only
from sqlalchemy import select,update,delete
from .shemas import RegisterRequestSchema,RegisterConfirmSchema,LoginRequestShema,LoginConfirmSchema
from data.db import get_session
from auth.models import User,RefreshToken
from .tools import hash_password,verify_password,create_access_token,decode_refresh_token,create_token

router = APIRouter(
    prefix='/user',
    tags=['user']
)



@router.post('/register')
async def create_user(
    data: Annotated[RegisterRequestSchema,Body()],
    session: Annotated[AsyncSession,Depends(get_session)]
):
    email = data.email
    username = data.username
    potential_user = await session.scalar(select(User)
        .where((User.email==email) | (User.username==username))
        .options(load_only(User.email,User.username))
    )
    if potential_user:
        errs = {}
        if potential_user.email==email:
            errs['email'] = 'The user with this email is already exists.'
        if potential_user.username==username:
            errs['username'] = 'The user with this username is already exists.'
        raise HTTPException(status_code=400,detail=errs)



@router.post('/register-confirm')
async def register_confirm(
    data: Annotated[RegisterConfirmSchema,Body()],
    session: Annotated[AsyncSession,Depends(get_session)]
):
    pass



@router.post('/login')
async def login_user(
    data: Annotated[LoginRequestShema,Body()],
    session: Annotated[AsyncSession,Depends(get_session)]
):
    email = data.email
    password = data.password
    potential_user = session.scalar(select(User)
        .where(User.email==email)
        .options(load_only(User.email,User.hashed_password))
    )
    if not potential_user or not verify_password(password,potential_user.hashed_password):
        raise HTTPException(status_code=400,detail='Invalid email or password')

    


@router.post('/login-confirm')
async def login_confirm(
    data: Annotated[LoginConfirmSchema,Body()],
    session: Annotated[AsyncSession,Depends(get_session)]
):
    pass



@router.post('/new-access')
async def update_access_token(
    request: Request,
    session: Annotated[AsyncSession,Depends(get_session)]
) -> dict[str,str]:
    
    refresh_token = request.cookies.get('refresh_token')

    if not refresh_token:
        raise HTTPException(status_code=403,detail='You have not refresh token. You must to login.')

    payload = await decode_refresh_token(refresh_token,session)

    user_id = int(payload.get('sub'))

    access_token = create_access_token(user_id)

    return {'access_token',access_token}



@router.post('/rotate-refresh')
async def rotate_refresh_token(
    request: Request,
    response: Response,
    session: Annotated[AsyncSession,Depends(get_session)]
) -> dict[str,str]:
    
    refresh_token = request.cookies.get('refresh_token')

    if not refresh_token:
        raise HTTPException(status_code=403,detail='You have not refresh token. You must to login.')

    payload = await decode_refresh_token(refresh_token,session)

    user_id = int(payload.get('sub'))

    jti = UUID(payload.get('jti'))

    new_refresh_token,new_payload = create_token(user_id,'refresh')

    new_expired_at = new_payload.get('exp')

    await session.execute(update(RefreshToken).where(RefreshToken.jti==jti).values(expired_at=new_expired_at))

    await session.commit()

    response.set_cookie(
        'refresh_token',
        new_refresh_token
    )

    return {'message':'refresh token successfuly rotated'}



@router.post('/logout')
async def logout(
    request: Request,
    session: Annotated[AsyncSession,Depends(get_session)]
) -> dict[str,str]:

    refresh_token = request.cookies.get('refresh_token')

    if not refresh_token:
        raise HTTPException(status_code=403,detail='You have not refresh token. You must to login.')

    payload = await decode_refresh_token(refresh_token,session)

    jti = UUID(payload.get('jti'))    

    await session.execute(delete(RefreshToken).where(RefreshToken.jti==jti))

    await session.commit()

    return {'message':'logout was successfult done'}



@router.post('/logout-all')
async def logout_all(
    request: Request,
    session: Annotated[AsyncSession,Depends(get_session)]
) -> dict[str,str]:

    refresh_token = request.cookies.get('refresh_token')

    if not refresh_token:
        raise HTTPException(status_code=403,detail='You have not refresh token. You must to login.')

    payload = await decode_refresh_token(refresh_token,session)

    user_id = int(payload.get('sub'))    

    await session.execute(delete(RefreshToken).where(RefreshToken.user_id==user_id))

    await session.commit()

    return {'message':'logout was successfult done'}
