# models/workout.py
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    JSON,
    DateTime,
    Interval,
    ForeignKey,
    Float,
    Integer,
    Boolean,
)
from datetime import timedelta
from sqlalchemy.orm import relationship
from datetime import datetime
from services.db import Base


class WorkoutTemplate(Base):
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


class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"

    id = Column(BigInteger, primary_key=True, index=True)
    template_id = Column(BigInteger, ForeignKey("workout_templates.id"), nullable=False)
    activity_id = Column(BigInteger, ForeignKey("Activities.id"), nullable=False)
    order = Column(BigInteger, nullable=False)
    rest_between_sets = Column(Interval)
    notes = Column(String(500))

    template = relationship("WorkoutTemplate", back_populates="exercises")
    activity = relationship("Activity")  # From previous activity model
    sets = relationship(
        "ExerciseSet", back_populates="exercise", cascade="all, delete-orphan"
    )


class ExerciseSet(Base):
    __tablename__ = "exercise_sets"

    id = Column(BigInteger, primary_key=True, index=True)
    exercise_id = Column(BigInteger, ForeignKey("workout_exercises.id"), nullable=False)
    set_number = Column(BigInteger, nullable=False)
    set_type = Column(String(20), nullable=False)  # normal, drop, super
    parameters = Column(
        JSON, nullable=False
    )  # {weight: [], reps: [], rpe: null, tempo: "3010"}

    exercise = relationship("WorkoutExercise", back_populates="sets")


class PerformedWorkout(Base):
    __tablename__ = "performed_workouts"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    template_id = Column(BigInteger, ForeignKey("workout_templates.id"))
    start_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime)
    paused_duration = Column(Interval, default=timedelta(0))
    status = Column(String(20), default="active")
    performance_metrics = Column(JSON)

    exercises = relationship(
        "PerformedExercise", back_populates="workout", cascade="all, delete-orphan"
    )


class PerformedExercise(Base):
    __tablename__ = "performed_exercises"

    id = Column(BigInteger, primary_key=True, index=True)
    workout_id = Column(BigInteger, ForeignKey("performed_workouts.id"), nullable=False)
    activity_id = Column(BigInteger, ForeignKey("Activities.id"), nullable=False)
    order = Column(Integer)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    rest_periods = Column(JSON)  # {between_sets: [timedelta]}

    workout = relationship("PerformedWorkout", back_populates="exercises")
    sets = relationship(
        "PerformedSet", back_populates="exercise", cascade="all, delete-orphan"
    )


class PerformedSet(Base):
    __tablename__ = "performed_sets"

    id = Column(BigInteger, primary_key=True, index=True)
    exercise_id = Column(
        BigInteger, ForeignKey("performed_exercises.id"), nullable=False
    )
    set_number = Column(Integer)
    weight = Column(Float)
    reps = Column(Integer)
    rpe = Column(Float)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    is_warmup = Column(Boolean, default=False)
    notes = Column(String(500))

    exercise = relationship("PerformedExercise", back_populates="sets")
