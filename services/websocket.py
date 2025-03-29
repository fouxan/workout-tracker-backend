from jose import JWTError, jwt
from fastapi import WebSocket, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.auth import User
from config import settings


async def authenticate_websocket(
    websocket: WebSocket, token: str, db: AsyncSession
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            raise ValueError

        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

        return user
    except (JWTError, ValueError):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
