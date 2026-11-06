from typing import Annotated
from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException,Body,Request,Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only,defer
from sqlalchemy import select,update,delete
from .shemas import RegisterRequestSchema,RegisterConfirmSchema,LoginRequestShema,LoginConfirmSchema
from data.db import get_session
from auth.models import User,RefreshToken
from .tools import hash_password,verify_password,create_access_token,decode_refresh_token,create_token,create_token_pair,RegisterManager,LoginManager

router = APIRouter(
    prefix='/user',
    tags=['user']
)



@router.post('/register')
async def create_user(
    data: Annotated[RegisterRequestSchema,Body()],
    session: Annotated[AsyncSession,Depends(get_session)]
) -> dict[str,str]:
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

    register_manager = RegisterManager(email)

    await register_manager.send_code(data)

    return {'message':'code was successfult sended'}



@router.post('/register-confirm',status_code=201)
async def register_confirm(
    data: Annotated[RegisterConfirmSchema,Body()],
    session: Annotated[AsyncSession,Depends(get_session)]
) -> dict[str,str]:
    email = data.email
    code = data.code



    register_manager = RegisterManager(email)

    username,email,password = await register_manager.verify_code(code)

    hashed_password = hash_password(password)

    user = User(email=email,username=username,hashed_password=hashed_password)

    session.add(user)

    await session.commit()

    return {'message':'the user successfult created. Now login.'}



@router.post('/login')
async def login_user(
    data: Annotated[LoginRequestShema,Body()],
    session: Annotated[AsyncSession,Depends(get_session)]
) -> dict[str,str]:
    email = data.email
    password = data.password
    potential_user = await session.scalar(select(User)
        .where(User.email==email)
        .options(defer(User.username))
    )
    if not potential_user or not verify_password(password,potential_user.hashed_password):
        raise HTTPException(status_code=400,detail='Invalid email or password')

    login_manager = LoginManager(email)

    await login_manager.send_code(potential_user.user_id)

    return {'message':'code was successfult sended'}
    


@router.post('/login-confirm')
async def login_confirm(
    data: Annotated[LoginConfirmSchema,Body()],
    response: Response,
    session: Annotated[AsyncSession,Depends(get_session)]
) -> dict[str,str]:
    email = data.email
    code = data.code

    login_manager = LoginManager(email)

    user_id = await login_manager.verify_code(code)

    tokens = await create_token_pair(user_id,session)

    refresh_token = tokens.pop('refresh_token')

    response.set_cookie(
        'refresh_token',
        refresh_token,
        max_age=3600*24*30,
        path='/user',
        httponly=True,
        samesite='lax'
    )

    return tokens # {'access_token':access_token}



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
        new_refresh_token,
        max_age=3600*24*30,
        path='/user',
        httponly=True,
        samesite='lax'
    )

    return {'message':'refresh token successfuly rotated'}



@router.post('/logout')
async def logout(
    request: Request,
    response: Response,
    session: Annotated[AsyncSession,Depends(get_session)]
) -> dict[str,str]:

    refresh_token = request.cookies.get('refresh_token')

    if not refresh_token:
        raise HTTPException(status_code=403,detail='You have not refresh token. You must to login.')

    payload = await decode_refresh_token(refresh_token,session)

    jti = UUID(payload.get('jti'))    

    await session.execute(delete(RefreshToken).where(RefreshToken.jti==jti))

    await session.commit()

    response.delete_cookie('refresh_token',path='/user',httponly=True)

    return {'message':'logout was successfult done'}



@router.post('/logout-all')
async def logout_all(
    request: Request,
    response: Response,
    session: Annotated[AsyncSession,Depends(get_session)]
) -> dict[str,str]:

    refresh_token = request.cookies.get('refresh_token')

    if not refresh_token:
        raise HTTPException(status_code=403,detail='You have not refresh token. You must to login.')

    payload = await decode_refresh_token(refresh_token,session)

    user_id = int(payload.get('sub'))    

    await session.execute(delete(RefreshToken).where(RefreshToken.user_id==user_id))

    await session.commit()

    response.delete_cookie('refresh_token',path='/user',httponly=True)

    return {'message':'logout was successfult done'}
