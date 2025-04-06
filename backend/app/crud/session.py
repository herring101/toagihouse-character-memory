import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.constants import (
    SESSION_STATUS_ACTIVE,
    SESSION_STATUS_COMPLETED,
    SESSION_TYPE_CONVERSATION,
    SESSION_TYPE_SLEEP,
)
from app.models import Session as DbSession


def create_session(
    db: Session,
    user_id: uuid.UUID,
    character_id: uuid.UUID,
    device_id: str,
    session_type: str,
    properties: Dict[str, Any] = None,
) -> DbSession:
    """
    新しいセッションを作成する。
    既にアクティブなセッションが存在する場合はエラーを返す。

    Args:
        db: データベースセッション
        user_id: ユーザーID
        character_id: キャラクターID
        device_id: デバイスID
        session_type: セッションタイプ ('conversation' または 'sleep')
        properties: セッションに関連する追加プロパティ (オプション)

    Returns:
        作成されたセッションのインスタンス

    Raises:
        HTTPException: 既にアクティブなセッションが存在する場合、またはデータベース操作中にエラーが発生した場合
    """
    if session_type not in [SESSION_TYPE_CONVERSATION, SESSION_TYPE_SLEEP]:
        raise ValueError(f"無効なセッションタイプです: {session_type}")

    try:
        # 既にアクティブなセッションが存在するか確認
        existing_sessions = (
            db.query(DbSession)
            .filter(DbSession.character_id == character_id, DbSession.is_active)
            .all()
        )

        if existing_sessions:
            raise HTTPException(
                status_code=409,
                detail=f"キャラクターID {character_id} には既にアクティブなセッションが存在します。"
                f"新しいセッションを開始する前に、既存のセッションを終了してください。",
            )

        # 新しいセッションを作成
        db_session = DbSession(
            user_id=user_id,
            character_id=character_id,
            device_id=device_id,
            session_type=session_type,
            is_active=True,
            status=SESSION_STATUS_ACTIVE,
            properties=properties or {},
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session

    except HTTPException:
        # HTTPExceptionは再スローする
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"セッション作成中にエラーが発生しました: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"予期せぬエラーが発生しました: {str(e)}"
        )


def get_active_session(db: Session, character_id: uuid.UUID) -> Optional[DbSession]:
    """
    キャラクターIDに基づいてアクティブなセッションを取得する

    Args:
        db: データベースセッション
        character_id: キャラクターID

    Returns:
        アクティブなセッションのインスタンス、見つからない場合はNone
    """
    return (
        db.query(DbSession)
        .filter(DbSession.character_id == character_id, DbSession.is_active)
        .first()
    )


def get_active_sessions_by_user(db: Session, user_id: uuid.UUID) -> List[DbSession]:
    """
    ユーザーIDに基づいてアクティブなセッションのリストを取得する

    Args:
        db: データベースセッション
        user_id: ユーザーID

    Returns:
        アクティブなセッションのリスト
    """
    return (
        db.query(DbSession)
        .filter(DbSession.user_id == user_id, DbSession.is_active)
        .all()
    )


def get_sessions_by_character(
    db: Session,
    character_id: uuid.UUID,
    active_only: bool = False,
    session_type: Optional[str] = None,
    limit: int = 100,
) -> List[DbSession]:
    """
    キャラクターIDに基づいてセッションのリストを取得する

    Args:
        db: データベースセッション
        character_id: キャラクターID
        active_only: アクティブなセッションのみを取得するかどうか
        session_type: 特定のセッションタイプでフィルタリング (オプション)
        limit: 取得するレコードの最大数

    Returns:
        セッションのリスト
    """
    query = db.query(DbSession).filter(DbSession.character_id == character_id)

    if active_only:
        query = query.filter(DbSession.is_active)

    if session_type:
        query = query.filter(DbSession.session_type == session_type)

    return query.order_by(DbSession.started_at.desc()).limit(limit).all()


def update_session(
    db: Session,
    session_id: uuid.UUID,
    is_active: Optional[bool] = None,
    status: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
) -> DbSession:
    """
    セッションを更新する

    Args:
        db: データベースセッション
        session_id: セッションID
        is_active: 新しいアクティブ状態 (オプション)
        status: 新しいステータス (オプション)
        properties: 更新するプロパティ (オプション、部分更新)

    Returns:
        更新されたセッションのインスタンス
    """
    try:
        db_session = db.query(DbSession).filter(DbSession.id == session_id).first()
        if db_session is None:
            raise HTTPException(status_code=404, detail="セッションが見つかりません")

        if is_active is not None:
            db_session.is_active = is_active

        if status is not None:
            db_session.status = status

        if properties is not None:
            # プロパティの部分更新 (既存のプロパティを保持)
            current_props = db_session.properties or {}
            current_props.update(properties)
            db_session.properties = current_props

        db_session.last_updated_at = datetime.now()

        db.commit()
        db.refresh(db_session)
        return db_session
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"セッション更新中にエラーが発生しました: {str(e)}"
        )


def end_session(
    db: Session,
    session_id: uuid.UUID,
    status: str = SESSION_STATUS_COMPLETED,
    properties: Optional[Dict[str, Any]] = None,
) -> DbSession:
    """
    セッションを終了する（非アクティブにする）

    Args:
        db: データベースセッション
        session_id: セッションID
        status: 終了時のステータス (デフォルト: 'completed')
        properties: 更新するプロパティ (オプション)

    Returns:
        更新されたセッションのインスタンス
    """
    return update_session(
        db, session_id, is_active=False, status=status, properties=properties
    )


def end_all_active_sessions(db: Session, character_id: uuid.UUID) -> int:
    """
    キャラクターに関連するすべてのアクティブなセッションを終了する

    Args:
        db: データベースセッション
        character_id: キャラクターID

    Returns:
        終了したセッションの数
    """
    try:
        active_sessions = (
            db.query(DbSession)
            .filter(DbSession.character_id == character_id, DbSession.is_active)
            .all()
        )

        count = 0
        for session in active_sessions:
            session.is_active = False
            session.status = SESSION_STATUS_COMPLETED
            session.last_updated_at = datetime.now()
            count += 1

        db.commit()
        return count
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"セッション終了中にエラーが発生しました: {str(e)}"
        )
