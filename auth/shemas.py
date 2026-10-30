from pydantic import BaseModel,EmailStr



class RegisterRequestSchema(BaseModel):
    username: str
    email: EmailStr
    password: str



class RegisterConfirmSchema(BaseModel):
    email: str
    code: str



class LoginRequestShema(BaseModel):
    email: str
    password: str



class LoginConfirmSchema(BaseModel):
    email: str
    code: str