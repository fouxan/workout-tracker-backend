from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from models.auth import PasswordResetOTP
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from services.db import get_db
from controllers.auth import get_user_by_email
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode |= {"exp": expire, "type": "access"}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode |= {"exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def hash_otp(otp: str):
    return pwd_context.hash(otp)


def verify_otp(plain_otp: str, hashed_otp: str):
    return pwd_context.verify(plain_otp, hashed_otp)


async def create_reset_otp(db: AsyncSession, user_id: int, expiry_minutes: int = 15):
    # Invalidate previous OTPs
    await db.execute(
        update(PasswordResetOTP)
        .where(PasswordResetOTP.user_id == user_id)
        .values(used=True)
    )

    raw_otp, expires_at = PasswordResetOTP.generate_otp(expiry_minutes)
    otp_record = PasswordResetOTP(
        user_id=user_id, otp_code=hash_otp(raw_otp), expires_at=expires_at
    )

    db.add(otp_record)
    await db.commit()
    return raw_otp


from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from services.auth import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload is None or payload.get("type") != "access":
            raise credentials_exception
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception from e

    user = await get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user
