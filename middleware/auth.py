from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from services.auth import decode_token
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from controllers.auth import get_user_by_email
from services.db import get_db


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
