# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.auth import (
    SignupRequest,
    AuthRequest,
    AuthResponse,
    RefreshRequest,
    ResetPasswordRequest,
    ChangePasswordRequest
)
from services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from controllers.auth import get_user_by_email, create_user
from services.db import get_db

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/signup", response_model=AuthResponse)
async def register_user(
    signup_request: SignupRequest,
    db: AsyncSession = Depends(get_db)
):
    # Check existing user
    existing_user = await get_user_by_email(db, signup_request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user = await create_user(db, signup_request)
    
    # Generate tokens
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})
    
    return AuthResponse(
        email=user.email,
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/login", response_model=AuthResponse)
async def login_user(
    auth_request: AuthRequest,
    db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_email(db, auth_request.email)
    if not user or not verify_password(auth_request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})
    
    return AuthResponse(
        email=user.email,
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/refresh", response_model=AuthResponse)
async def refresh_token_endpoint(refresh_request: RefreshRequest):
    payload = decode_token(refresh_request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    new_access = create_access_token({"sub": payload.get("sub")})
    return AuthResponse(
        email=payload.get("sub"),
        access_token=new_access,
        refresh_token=refresh_request.refresh_token
    )

@router.post("/reset-password")
async def reset_password(
    reset_request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    payload = decode_token(reset_request.token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )

    user = await get_user_by_email(db, payload.get("sub"))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.password = hash_password(reset_request.new_password)
    await db.commit()
    return {"message": "Password reset successful"}

@router.post("/change-password")
async def change_password(
    email: str,
    request: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_email(db, email)
    if not user or not verify_password(request.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid old password"
        )

    user.password = hash_password(request.new_password)
    await db.commit()
    return {"message": "Password changed successfully"}


@router.get("/forgot-password", response_model=AuthResponse)
async def forgot_password(
    email: str,
    db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    reset_token = create_access_token({"sub": user.email, "type": "reset"})
    
    # Here you would send the token to the user's email
    # For demonstration, we will just return it
    return {"reset_token": reset_token}

@router.post("/verify-token")
async def verify_token(
    token: str
):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )
    
    return {"message": "Token is valid", "email": payload.get("sub")}