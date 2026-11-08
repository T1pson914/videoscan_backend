import aiosmtplib
import os
import secrets
from fastapi import HTTPException
from email.message import EmailMessage
from core.cache import redis_conn
from auth.shemas import RegisterRequestSchema



LOGIN_CODE_KEY = 'login_data'
REGISTER_CODE_KEY = 'register_data'
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_HOST = os.getenv('EMAIL_HOST')



class Manager:



    def __init__(self,email:str, key:str) -> None:
        self.email = email
        self.key = key



    def build_message(self,subject:str, content:str) -> EmailMessage:

        message = EmailMessage()
        message['To'] = self.email
        message['From'] = EMAIL_USER
        message['Subject'] = subject
        message.set_content(content)

        return message



    async def send_message(self,subject:str, content:str) -> bool:

        message = self.build_message(subject,content)

        try:
            print(EMAIL_PASSWORD)
            await aiosmtplib.send(
                message,
                hostname=EMAIL_HOST,
                password=EMAIL_PASSWORD,
                username=EMAIL_USER,
                port=465,
                use_tls=True
            )
        except aiosmtplib.SMTPException:
            return False

        return True



class RegisterManager(Manager):



    def __init__(self, email) -> None:
        super().__init__(email=email, key=f'{REGISTER_CODE_KEY}:{email}')



    async def send_code(self,data:RegisterRequestSchema) -> None:

        register_data = await redis_conn.hgetall(self.key)
        if register_data:
            return
        
        code = secrets.randbelow(900_000) + 100_000

        await self.send_message(
            subject='Confirm your registration on VideoScan.',
            content=f'Your code to confirm: {code}'
        )        

        user_data = data.model_dump()

        register_data = {'code':code,'tries':5,**user_data}

        await redis_conn.hset(self.key,mapping=register_data)

        await redis_conn.expire(self.key,90)



    async def verify_code(self, entered_code:int) -> dict[str,str]:
        register_data = await redis_conn.hgetall(self.key)
        code = register_data.get('code')
        tries = int(register_data.get('tries',0))
        if tries==0:
            await redis_conn.delete(self.key)
            raise HTTPException(status_code=403,detail='Number of attempts exhausted')
        if entered_code!=code:
            tries -= 1
            await redis_conn.hset(self.key,'tries',tries)
            raise HTTPException(status_code=400,detail='Invalid code.')
        await redis_conn.delete(self.key)
        register_data.pop('code')
        register_data.pop('tries')
        return tuple(register_data.values())



class LoginManager(Manager):



    def __init__(self, email) -> None:
        super().__init__(email=email, key=f'{LOGIN_CODE_KEY}:{email}')



    async def send_code(self, user_id:int) -> None:

        login_data = await redis_conn.hgetall(self.key)
        if login_data:
            return
        
        code = secrets.randbelow(900_000) + 100_000

        await self.send_message(
            subject='Confirm your login on VideoScan.',
            content=f'Your code to confirm: {code}'
        )        

        login_data = {'code':code,'tries':5,'user_id':user_id}

        await redis_conn.hset(self.key,mapping=login_data)

        await redis_conn.expire(self.key,90)



    async def verify_code(self, entered_code:int) -> int:
        login_data = await redis_conn.hgetall(self.key)
        code = login_data.get('code')
        tries = int(login_data.get('tries',0))
        if tries==0:
            await redis_conn.delete(self.key)
            raise HTTPException(status_code=403,detail='Number of attempts exhausted')
        if entered_code!=code:
            tries -= 1
            await redis_conn.hset(self.key,'tries',tries)
            raise HTTPException(status_code=400,detail='Invalid code.')
        await redis_conn.delete(self.key)
        user_id = login_data.get('user_id')
        return user_id
