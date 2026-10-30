from typing import Annotated
from fastapi import APIRouter,Depends,HTTPException,Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .shemas import RegisterRequestSchema,RegisterConfirmSchema,LoginRequestShema,LoginConfirmSchema
from data.db import get_session
from auth.models import User,RefreshToken


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
    potential_user = await session.scalar(select(User).where((User.email==email) | (User.username==username)))
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
