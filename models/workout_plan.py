# models/plan.py
from sqlalchemy import Column, BigInteger, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from services.db import Base
from datetime import date


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(Date, default=date.today)

    days = relationship("PlanDay", back_populates="plan", cascade="all, delete-orphan")


class PlanDay(Base):
    __tablename__ = "plan_days"

    id = Column(BigInteger, primary_key=True, index=True)
    plan_id = Column(BigInteger, ForeignKey("workout_plans.id"), nullable=False)
    day_number = Column(BigInteger, nullable=False)
    focus_area = Column(String(100))
    notes = Column(String(500))

    plan = relationship("WorkoutPlan", back_populates="days")
    scheduled_workouts = relationship(
        "ScheduledWorkout", back_populates="day", cascade="all, delete-orphan"
    )


class ScheduledWorkout(Base):
    __tablename__ = "scheduled_workouts"

    id = Column(BigInteger, primary_key=True, index=True)
    day_id = Column(BigInteger, ForeignKey("plan_days.id"), nullable=False)
    template_id = Column(BigInteger, ForeignKey("workout_templates.id"), nullable=False)
    scheduled_time = Column(String(5))  # HH:MM format
    is_completed = Column(Boolean, default=False)

    day = relationship("PlanDay", back_populates="scheduled_workouts")
    template = relationship("WorkoutTemplate")
