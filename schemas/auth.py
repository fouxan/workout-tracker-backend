from pydantic import BaseModel, EmailStr

class SignupRequest(BaseModel):
    email: EmailStr
    password: str

class AuthRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class AuthResponse(BaseModel):
    email: str
    access_token: str
    refresh_token: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr
    otp: int
    new_password: str