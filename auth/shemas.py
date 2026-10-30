from pydantic import BaseModel,EmailStr



class RegisterRequestSchema(BaseModel):
    username: str
    email: EmailStr
    password: str



class RegisterConfirmSchema(BaseModel):
    email: str
    code: str