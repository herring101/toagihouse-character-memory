from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
import uuid
from typing import Optional

from app.models import Memory

def add_memory(db: Session, user_id: uuid.UUID, character_id: uuid.UUID, memory_type: str, 
               start_day: int, end_day: int, content: str):
    """
    新しい記憶を追加する
    
    Args:
        db: データベースセッション
        user_id: ユーザーID
        character_id: キャラクターID
        memory_type: 記憶タイプ ('daily_raw', 'daily_summary', 'level_10', 'level_100', 'level_1000', 'level_archive')
        start_day: 開始日
        end_day: 終了日
        content: 記憶内容
    
    Returns:
        作成された記憶のインスタンス
    """
    try:
        db_memory = Memory(
            user_id=user_id,
            character_id=character_id,
            memory_type=memory_type,
            start_day=start_day,
            end_day=end_day,
            content=content
        )
        db.add(db_memory)
        db.commit()
        db.refresh(db_memory)
        return db_memory
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"記憶追加中にエラーが発生しました: {str(e)}")

def get_memories_by_character(
    db: Session, character_id: uuid.UUID, memory_type: Optional[str] = None, 
    start_day: Optional[int] = None, end_day: Optional[int] = None,
    skip: int = 0, limit: int = 100
):
    """
    キャラクターIDと条件に基づいて記憶を取得する
    
    Args:
        db: データベースセッション
        character_id: キャラクターID
        memory_type: 記憶タイプでフィルタリング（オプション）
        start_day: 開始日でフィルタリング（オプション）
        end_day: 終了日でフィルタリング（オプション）
        skip: スキップするレコード数
        limit: 取得するレコードの最大数
    
    Returns:
        記憶のリスト
    """
    query = db.query(Memory).filter(Memory.character_id == character_id)
    
    if memory_type:
        query = query.filter(Memory.memory_type == memory_type)
    
    if start_day is not None:
        query = query.filter(Memory.start_day >= start_day)
    
    if end_day is not None:
        query = query.filter(Memory.end_day <= end_day)
    
    return query.order_by(Memory.start_day.desc()).offset(skip).limit(limit).all()

def update_memory(db: Session, memory_id: uuid.UUID, content: Optional[str] = None, memory_type: Optional[str] = None):
    """
    記憶を更新する
    
    Args:
        db: データベースセッション
        memory_id: 記憶ID
        content: 新しい記憶内容（オプション）
        memory_type: 新しい記憶タイプ（オプション）
    
    Returns:
        更新された記憶のインスタンス
    """
    try:
        db_memory = db.query(Memory).filter(Memory.id == memory_id).first()
        if db_memory is None:
            raise HTTPException(status_code=404, detail="記憶が見つかりません")
        
        if content is not None:
            db_memory.content = content
        
        if memory_type is not None:
            db_memory.memory_type = memory_type
        
        db.commit()
        db.refresh(db_memory)
        return db_memory
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"記憶更新中にエラーが発生しました: {str(e)}")

def delete_memory(db: Session, memory_id: uuid.UUID):
    """
    記憶を削除する
    
    Args:
        db: データベースセッション
        memory_id: 記憶ID
    
    Returns:
        削除が成功したかどうか
    """
    try:
        db_memory = db.query(Memory).filter(Memory.id == memory_id).first()
        if db_memory is None:
            raise HTTPException(status_code=404, detail="記憶が見つかりません")
        
        db.delete(db_memory)
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"記憶削除中にエラーが発生しました: {str(e)}")
