"""Wzorce klas dla FitApp (API)."""

from sqlmodel import SQLModel, Field
from typing import Optional, Literal
from pydantic import EmailStr, SecretStr, BaseModel
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"

    @classmethod
    def from_string(cls, gender_string: str):
        gender_string = gender_string.upper()
        if gender_string == "MALE":
            return cls.MALE
        elif gender_string == "FEMALE":
            return cls.FEMALE
        else:
            raise ValueError(f"Nieprawidłowa wartość płci: {gender_string}. Dozwolone wartości to 'male' lub 'female'.")

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    last_name: str
    email: EmailStr
    hashed_password: str
    is_admin: bool = Field(default=False)
    details: Optional["UserDetails"] = Relationship(back_populates="user")

class UserDetails(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    weight: Optional[float] = Field(ge=0, default=None)
    height: Optional[int] = Field(ge=0, default=None)
    age: Optional[int] = Field(ge=0, default=None)
    gender: Optional[Gender] = Field(default=None)
    user: Optional["User"] = Relationship(back_populates="details")


class UserFcmID(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    fcm_push_token: Optional[str] = Field(default=None)

class UserCreate(BaseModel):
    name: str
    last_name: str
    email: EmailStr
    password: SecretStr
    is_admin: bool = False
    weight: Optional[float] = None
    height: Optional[int] = None
    age: Optional[int] = None
    gender: Optional[Gender] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: SecretStr


class UserDetailsResponse(BaseModel):
    weight: Optional[float] = None
    height: Optional[int] = None
    age: Optional[int] = None
    gender: Optional[Gender] = None

    class Config:
        from_attributes = True
        use_enum_values = True 

class UserResponse(BaseModel):
    id: int
    name: str
    last_name: str
    email: EmailStr
    is_admin: bool
    details: Optional[UserDetailsResponse] = None

    class Config:
        from_attributes = True

