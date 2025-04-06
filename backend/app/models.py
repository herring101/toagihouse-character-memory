import uuid

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.database import Base


class Character(Base):
    """キャラクターモデル

    キャラクターの基本情報を保存する。
    """

    __tablename__ = "characters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    config = Column(JSON, default={})
    is_sleeping = Column(Boolean, default=False)
    last_memory_processing_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Memory(Base):
    """記憶モデル

    階層化された記憶データを保存する。
    """

    __tablename__ = "memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    character_id = Column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
    )
    memory_type = Column(String, nullable=False)
    start_day = Column(Integer, nullable=False)
    end_day = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Session(Base):
    """セッションモデル

    会話セッションや睡眠セッションの情報を保存する。
    セッションはキャラクターごとに1つだけアクティブにできる。
    """

    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    character_id = Column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
    )
    device_id = Column(String, nullable=False)
    session_type = Column(String, nullable=False)  # 'conversation' または 'sleep'
    is_active = Column(Boolean, nullable=False, default=True)
    status = Column(
        String, nullable=False, default="active"
    )  # 'active', 'completed', 'error'
    properties = Column(JSON, default={})  # 追加データを保存するためのJSONフィールド
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
