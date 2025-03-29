# models/workout.py
from sqlalchemy import Column, BigInteger, String, JSON, DateTime, Interval, ForeignKey
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
