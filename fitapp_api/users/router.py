from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fitapp_api.users.models import User, UserCreate, UserResponse
from fitapp_api.postgres.db import PostgresDB
import os
from dotenv import load_dotenv

load_dotenv()

user_router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 300))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
    statement = select(User).where(User.email == email)
    result = await db.execute(statement)
    return result.scalar_one_or_none()

async def authenticate_user(email: str, password: str, db: AsyncSession) -> Optional[User]:
    user = await get_user_by_email(email, db)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(PostgresDB().get_session)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nie można zweryfikować danych logowania.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user_by_email(email, db)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.isAdmin:
        raise HTTPException(status_code=403, detail="Brak autoryzacji do chronionego zasobu.")
    return current_user

# Endpointy
@user_router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(PostgresDB().get_session)):
    if await get_user_by_email(user_data.email, db):
        raise HTTPException(status_code=400, detail="Konto z tym adresem emailem już istnieje!")
    hashed_password = get_password_hash(user_data.password.get_secret_value())
    new_user = User(
        name=user_data.name,
        last_name=user_data.last_name,
        email=user_data.email,
        hashed_password=hashed_password,
        isAdmin=False
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@user_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(PostgresDB().get_session)):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=400, detail="Nieprawidłowy adres email lub hasło!")
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@user_router.post("/logout")
async def logout():
    return {"message": "Pomyślnie wylogowano!"}

@user_router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@user_router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, current_user: User = Depends(get_current_admin_user), db: AsyncSession = Depends(PostgresDB().get_session)):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Podany użytkownik nie istnieje!")
    return user

@user_router.delete("/users/{user_id}")
async def delete_user(user_id: int, current_user: User = Depends(get_current_admin_user), db: AsyncSession = Depends(PostgresDB().get_session)):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Podany użytkownik nie istnieje!")
    await db.delete(user)
    await db.commit()
    return {"message": "Pomyślnie usunięto użytkownika!"}

@user_router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Witaj, {current_user.name}! To chroniony endpoint."}
