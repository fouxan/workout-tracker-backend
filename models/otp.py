from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
import secrets

Base = declarative_base()
