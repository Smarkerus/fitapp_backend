"""Wzorce klas dla FitApp (API)."""

from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import EmailStr, SecretStr, BaseModel

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    last_name: str
    email: EmailStr
    hashed_password: str
    isAdmin: bool = Field(default=False)

class UserCreate(BaseModel):
    name: str
    last_name: str
    email: EmailStr
    password: SecretStr

class UserLogin(BaseModel):
    email: EmailStr
    password: SecretStr

class UserResponse(BaseModel):
    id: int
    name: str
    last_name: str
    email: EmailStr
    isAdmin: bool