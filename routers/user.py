# routers/auth.py
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from models.auth import PasswordResetOTP, User
from schemas.auth import (
    PasswordResetRequest,
    SignupRequest,
    AuthRequest,
    AuthResponse,
    RefreshRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
)
from services.auth import (
    create_reset_otp,
    hash_password,
    verify_otp,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from controllers.auth import get_user_by_email, create_user
from services.db import get_db
import datetime
from sqlalchemy import select

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=AuthResponse)
async def register_user(
    signup_request: SignupRequest, db: AsyncSession = Depends(get_db)
):
    # Check existing user
    existing_user = await get_user_by_email(db, signup_request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create user
    user = await create_user(db, signup_request)

    # Generate tokens
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    return AuthResponse(
        email=user.email, access_token=access_token, refresh_token=refresh_token
    )


@router.post("/login", response_model=AuthResponse)
async def login_user(auth_request: AuthRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, auth_request.email)
    if not user or not verify_password(auth_request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    return AuthResponse(
        email=user.email, access_token=access_token, refresh_token=refresh_token
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token_endpoint(refresh_request: RefreshRequest):
    payload = decode_token(refresh_request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    new_access = create_access_token({"sub": payload.get("sub")})
    return AuthResponse(
        email=payload.get("sub"),
        access_token=new_access,
        refresh_token=refresh_request.refresh_token,
    )


@router.post("/reset-password")
async def reset_password(
    reset_request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)
):
    payload = decode_token(reset_request.token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )

    user = await get_user_by_email(db, payload.get("sub"))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.password = hash_password(reset_request.new_password)
    await db.commit()
    return {"message": "Password reset successful"}


@router.post("/change-password")
async def change_password(
    email: str, request: ChangePasswordRequest, db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_email(db, email)
    if not user or not verify_password(request.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid old password"
        )

    user.password = hash_password(request.new_password)
    await db.commit()
    return {"message": "Password changed successfully"}


@router.get("/forgot-password", response_model=AuthResponse)
async def forgot_password(
    email: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_email(db, email)
    if not user:
        return {"message": "If this email is registered, a reset OTP will be sent."}

    raw_otp = await create_reset_otp(db, user.id)

    # background_tasks.add_task(
    #     send_otp_email, email, raw_otp
    # )
    return {"otp": raw_otp, "message": "OTP sent to your email."}


@router.post("/verify-otp")
async def verify_otp_and_reset(
    request: PasswordResetRequest, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(PasswordResetOTP)
        .join(User)
        .where(
            User.email == request.email,
            PasswordResetOTP.expires_at > datetime.now(),
            PasswordResetOTP.used == False,
        )
    )

    otp_record = result.scalar_one_or_none()
    if not otp_record or not verify_otp(request.otp, otp_record.otp_code):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Update password
    user = await get_user_by_email(db, request.email)
    user.password = hash_password(request.new_password)

    # Mark OTP as used
    otp_record.used = True

    await db.commit()
    return {"message": "Password reset successful"}
