from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from database import Base

class Character(Base):
    __tablename__ = "characters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    config = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Memory(Base):
    __tablename__ = "memories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    memory_type = Column(String, nullable=False)
    start_day = Column(Integer, nullable=False)
    end_day = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    device_id = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
