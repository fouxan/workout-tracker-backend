from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import os
from typing import Optional, Tuple
from config import supabase


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        self.supabase = supabase
    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        credentials = await super().__call__(request)
        try:
            user = await self.verify_jwt(credentials.credentials)
            request.state.user = user
            return user
        except HTTPException:
            if self.auto_error:
                raise
            return None
    async def verify_jwt(self, token: str) -> dict:
        try:
            # Then validate with Supabase
            user = self.supabase.auth.get_user(token)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                )
            return {
                "id": user.user.id,
                "email": user.user.email,
                "token": token
            }
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

async def get_current_user(
    user: HTTPAuthorizationCredentials = Depends(JWTBearer(auto_error=False))
) -> dict:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authorization header missing",
        )
    return user