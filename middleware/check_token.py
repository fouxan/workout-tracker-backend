from fastapi import HTTPException, Header, Depends
from jose import jwt, JWTError
from functools import wraps
from typing import Callable
from fastapi import Request

# JWT Configurations
JWT_SECRET = "your_jwt_secret"  # Replace with your secret or load from .env
JWT_ALGORITHM = "HS256"

def protected(func: Callable):
    """
    A decorator to protect routes by checking the validity of a JWT token.
    """
    @wraps(func)
    async def wrapper(*args, request: Request, authorization: str = Header(...), **kwargs):
        try:
            # Extract token from Authorization header
            if not authorization.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Invalid Authorization header format")

            token = authorization.split(" ")[1]  # Get token part
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            email = payload.get("email")
            if not email:
                raise HTTPException(status_code=401, detail="Invalid token: email missing")
            
            # Pass the validated email to the route handler (optional)
            request.state.user_email = email

        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return await func(*args, **kwargs)
    
    return wrapper
