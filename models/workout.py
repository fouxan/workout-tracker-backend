# models/workout.py
from sqlalchemy import (
    UUID,
    Column,
    BigInteger,
    String,
    DateTime,
    ForeignKey,
    Float,
    Integer,
    Boolean,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from services.db import Base


class ActivitySets(Base):
    __tablename__ = "activity_sets"

    id = Column(UUID, primary_key=True, index=True)
    template_activity_id = Column(
        UUID, ForeignKey("workout_template_activities.id"), nullable=True
    )
    session_activity_id = Column(
        UUID, ForeignKey("workout_session_activities.id"), nullable=True
    )
    reps = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    duration = Column(Float, nullable=True)
    rpe = Column(Float, nullable=True)
    pace = Column(Float, nullable=True)
    heart_rate = Column(Float, nullable=True)
    is_active = Column(Boolean, default=False)
    notes = Column(String, nullable=True)
    rest_after_set = Column(Float, nullable=True)
    set_number = Column(Integer, nullable=False)
    is_warmup = Column(Boolean, default=False)
    is_cooldown = Column(Boolean, default=False)
    set_type = Column(String, nullable=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    # Relationships
    template_activity = relationship("WorkoutTemplateActivity", back_populates="sets")
    session_activity = relationship("WorkoutSessionActivity", back_populates="sets")
    __table_args__ = (
        {
            "sqlite_autoincrement": True,
            "extend_existing": True,
        },
    )


class WorkoutSessionActivities(Base):
    __tablename__ = "workout_session_activities"
    id = Column(UUID, primary_key=True, index=True)
    activity_id = Column(String, nullable=False)
    session_id = Column(UUID, ForeignKey("workout_sessions.id"), nullable=False)
    notes = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)

    # Relationships
    session = relationship("WorkoutSession", back_populates="activities")
    sets = relationship(
        "ActivitySet", back_populates="session_activity", cascade="all, delete-orphan"
    )
    __table_args__ = (
        {
            "sqlite_autoincrement": True,
            "extend_existing": True,
        },
    )


class WorkoutTemplateActivities(Base):
    __tablename__ = "workout_template_activities"

    id = Column(UUID, primary_key=True, index=True)
    activity_id = Column(String, nullable=False)
    template_id = Column(UUID, ForeignKey("workout_templates.id"), nullable=False)
    order = Column(Integer, nullable=False)
    notes = Column(String, nullable=True)

    # Relationships
    template = relationship("WorkoutTemplate", back_populates="exercises")
    sets = relationship(
        "ActivitySet", back_populates="template_activity", cascade="all, delete-orphan"
    )


class WorkoutTemplates(Base):
    __tablename__ = "workout_templates"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)

    exercises = relationship(
        "WorkoutExercise", back_populates="template", cascade="all, delete-orphan"
    )


class WorkoutSessions(Base):
    __tablename__ = "workout_sessions"

    id = Column(UUID, primary_key=True, index=True)
    template_id = Column(UUID, ForeignKey("workout_templates.id"), nullable=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    status = Column(
        String,
        nullable=False,
        default="draft",
        server_default="draft",
    )
    notes = Column(String(500))
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    calories_burnt = Column(Float, nullable=True)

    # Relationships
    user = relationship("User", back_populates="workout_sessions")
    template = relationship("WorkoutTemplate", back_populates="sessions")
    activities = relationship(
        "WorkoutSessionActivity", back_populates="session", cascade="all, delete-orphan"
    )
    __table_args__ = (
        {
            "sqlite_autoincrement": True,
            "extend_existing": True,
        },
    )


class WorkoutPlans(Base):
    __tablename__ = "workout_plans"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)

    templates = relationship(
        "WorkoutTemplate", back_populates="workout_plan", cascade="all, delete-orphan"
    )
