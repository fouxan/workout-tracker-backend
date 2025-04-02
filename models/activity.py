from sqlalchemy import (
    UUID,
    Column,
    BigInteger,
    Float,
    ForeignKey,
    SmallInteger,
    String,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Activity(Base):
    __tablename__ = "activities"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    force = Column(String, nullable=False)
    level = Column(String, nullable=False)
    mechanic = Column(String, nullable=False)
    equipment = Column(String, nullable=False)
    primary_muscles = Column(JSON, nullable=False)
    secondary_muscles = Column(JSON, nullable=False)
    instructions = Column(JSON, nullable=False)
    category = Column(String, nullable=False)
    images = Column(JSON, nullable=False)


class ActivityRecords(Base):
    __tablename__ = "activity_records"
    id = Column(BigInteger, primary_key=True, index=True)
    activity_id = Column(String, ForeignKey("activities.id"), nullable=False)
    user_id = Column(UUID, ForeignKey("user.id"), nullable=False)
    max_weight = Column(Float, nullable=True)
    max_reps = Column(SmallInteger, nullable=True)
    max_duration = Column(Float, nullable=True)
    max_rpe = Column(Float, nullable=True)
    max_heart_rate = Column(Float, nullable=True)
    max_pace = Column(Float, nullable=True)
    times_performed = Column(SmallInteger, default=0)
    recorded_at = Column(String, nullable=False)
