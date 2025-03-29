from sqlalchemy import Column, BigInteger, String, ForeignKey, JSON, Float, Boolean
import datetime
import secrets
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import timedelta

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    plan = Column(String, nullable=False)

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    plans = relationship("UserPlan", back_populates="user")


class UserProfile(Base):
    __tablename__ = "userprofile"
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    weight = Column(Float(53), nullable=False)
    height = Column(Float(53), nullable=False)
    experience_level = Column(String, nullable=False)
    dietary_restrictions = Column(JSON, nullable=False)

    user = relationship("User", back_populates="profile")


class UserPlan(Base):
    __tablename__ = "userplans"
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    plan = Column(BigInteger, nullable=False)
    expires_on = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="plans")


class PasswordResetOTP(Base):
    __tablename__ = "password_reset_otps"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    otp_code = Column(String, nullable=False)  # Store hashed OTP
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)

    @staticmethod
    def generate_otp(expiry_minutes: int = 15):
        otp = secrets.randbelow(1_000_000)  # 6-digit code
        expires_at = datetime.now() + timedelta(minutes=expiry_minutes)
        return str(otp).zfill(6), expires_at
