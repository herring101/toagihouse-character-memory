from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
import uuid
from typing import Optional, Dict, Any

from app.models import Character

def create_character(db: Session, user_id: uuid.UUID, name: str, config: Dict[str, Any] = {}):
    """
    新しいキャラクターを作成する
    
    Args:
        db: データベースセッション
        user_id: ユーザーID
        name: キャラクター名
        config: キャラクター設定（オプション）
    
    Returns:
        作成されたキャラクターのインスタンス
    """
    try:
        db_character = Character(user_id=user_id, name=name, config=config)
        db.add(db_character)
        db.commit()
        db.refresh(db_character)
        return db_character
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"キャラクター作成中にエラーが発生しました: {str(e)}")

def get_character(db: Session, character_id: uuid.UUID):
    """
    キャラクターIDでキャラクターを取得する
    
    Args:
        db: データベースセッション
        character_id: キャラクターID
    
    Returns:
        キャラクターのインスタンス、見つからない場合はNone
    """
    return db.query(Character).filter(Character.id == character_id).first()

def get_characters_by_user(db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100):
    """
    ユーザーIDに基づいてキャラクターのリストを取得する
    
    Args:
        db: データベースセッション
        user_id: ユーザーID
        skip: スキップするレコード数
        limit: 取得するレコードの最大数
    
    Returns:
        キャラクターのリスト
    """
    return db.query(Character).filter(Character.user_id == user_id).offset(skip).limit(limit).all()

def update_character(db: Session, character_id: uuid.UUID, name: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
    """
    キャラクターを更新する
    
    Args:
        db: データベースセッション
        character_id: キャラクターID
        name: 新しいキャラクター名（オプション）
        config: 新しいキャラクター設定（オプション）
    
    Returns:
        更新されたキャラクターのインスタンス
    """
    try:
        db_character = db.query(Character).filter(Character.id == character_id).first()
        if db_character is None:
            raise HTTPException(status_code=404, detail="キャラクターが見つかりません")
        
        if name is not None:
            db_character.name = name
        
        if config is not None:
            db_character.config = config
        
        db.commit()
        db.refresh(db_character)
        return db_character
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"キャラクター更新中にエラーが発生しました: {str(e)}")

def delete_character(db: Session, character_id: uuid.UUID):
    """
    キャラクターを削除する
    
    Args:
        db: データベースセッション
        character_id: キャラクターID
    
    Returns:
        削除が成功したかどうか
    """
    try:
        db_character = db.query(Character).filter(Character.id == character_id).first()
        if db_character is None:
            raise HTTPException(status_code=404, detail="キャラクターが見つかりません")
        
        db.delete(db_character)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"キャラクター削除中にエラーが発生しました: {str(e)}")
