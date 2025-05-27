

from pydantic import BaseModel


class UserRole(BaseModel):
    user_id: int
    role_id: int


class UserCreate(BaseModel):
    username: str
    password: str
    email: str | None = None
    

class UserLogin(BaseModel):
    username: str
    password: str