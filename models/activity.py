from sqlalchemy import Column, BigInteger, String, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Activity(Base):
    __tablename__ = "Activities"

    id = Column(BigInteger, primary_key=True, index=True)
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
