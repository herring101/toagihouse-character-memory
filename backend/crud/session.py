from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
import uuid
from datetime import datetime
from typing import Optional

from models import Session as DbSession

def create_session(db: Session, user_id: uuid.UUID, character_id: uuid.UUID, device_id: str):
    """
    新しいセッションを作成する
    
    Args:
        db: データベースセッション
        user_id: ユーザーID
        character_id: キャラクターID
        device_id: デバイスID
    
    Returns:
        作成されたセッションのインスタンス
    """
    try:
        existing_sessions = db.query(DbSession).filter(
            DbSession.character_id == character_id,
            DbSession.device_id == device_id,
            DbSession.is_active == True
        ).all()
        
        for session in existing_sessions:
            session.is_active = False
            session.last_updated_at = datetime.now()
        
        db_session = DbSession(
            user_id=user_id,
            character_id=character_id,
            device_id=device_id,
            is_active=True
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"セッション作成中にエラーが発生しました: {str(e)}")

def get_active_session(db: Session, character_id: uuid.UUID, device_id: str):
    """
    キャラクターIDとデバイスIDに基づいてアクティブなセッションを取得する
    
    Args:
        db: データベースセッション
        character_id: キャラクターID
        device_id: デバイスID
    
    Returns:
        アクティブなセッションのインスタンス、見つからない場合はNone
    """
    return db.query(DbSession).filter(
        DbSession.character_id == character_id,
        DbSession.device_id == device_id,
        DbSession.is_active == True
    ).first()

def update_session(db: Session, session_id: uuid.UUID, is_active: Optional[bool] = None):
    """
    セッションを更新する
    
    Args:
        db: データベースセッション
        session_id: セッションID
        is_active: 新しいアクティブ状態（オプション）
    
    Returns:
        更新されたセッションのインスタンス
    """
    try:
        db_session = db.query(DbSession).filter(DbSession.id == session_id).first()
        if db_session is None:
            raise HTTPException(status_code=404, detail="セッションが見つかりません")
        
        if is_active is not None:
            db_session.is_active = is_active
        
        db_session.last_updated_at = datetime.now()
        
        db.commit()
        db.refresh(db_session)
        return db_session
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"セッション更新中にエラーが発生しました: {str(e)}")

def end_session(db: Session, session_id: uuid.UUID):
    """
    セッションを終了する（非アクティブにする）
    
    Args:
        db: データベースセッション
        session_id: セッションID
    
    Returns:
        更新されたセッションのインスタンス
    """
    return update_session(db, session_id, is_active=False)
