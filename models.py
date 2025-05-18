import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import enum

Base = declarative_base()

class Priority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, nullable=False)
    message_text = Column(String, nullable=False)
    response_text = Column(Text, nullable=True)
    status = Column(String, default="new")
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    timestamp = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    agent_id = Column(Integer, nullable=True)

# Fetch the DATABASE_URL from the environment variable (Render will automatically set it)
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:samson.in@localhost:5432/mydb')  # Fallback for local development

# Create the SQLAlchemy engine for PostgreSQL
engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"} if "neon" in DATABASE_URL else {})

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
