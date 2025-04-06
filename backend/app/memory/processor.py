import uuid
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.core.constants import (
    MEMORY_TYPE_LEVEL_10,
    MEMORY_TYPE_LEVEL_100,
    MEMORY_TYPE_LEVEL_1000,
    MEMORY_TYPE_LEVEL_ARCHIVE,
    SESSION_STATUS_COMPLETED,
    SESSION_STATUS_ERROR,
    SESSION_TYPE_SLEEP,
)
from app.crud import memory as memory_crud
from app.crud.session import create_session, end_session
from app.memory.generator import MemoryGenerator
from app.models import Character, Memory


class SleepProcessor:
    """睡眠処理エンジン

    睡眠セッション中に記憶の処理と階層的要約を行う。
    """

    def __init__(
        self,
        db: Session,
        character_id: uuid.UUID,
        model: str = "gemini/gemini-2.0-flash",
    ):
        """
        睡眠中の記憶処理エンジンの初期化

        Args:
            db: データベースセッション
            character_id: キャラクターID
            model: 使用するLLMモデル
        """
        self.db = db
        self.character_id = character_id
        self.model = model
        self.memory_generator = MemoryGenerator(db, character_id, model)

        self.character = (
            db.query(Character).filter(Character.id == character_id).first()
        )
        if not self.character:
            raise ValueError(f"キャラクターID {character_id} が見つかりません")
        self.user_id = self.character.user_id

    def process_daily_memories(self, current_day: int) -> List[Memory]:
        """
        睡眠セッション中に記憶を処理する

        Args:
            current_day: 現在の日

        Returns:
            処理された記憶のリスト
        """
        processed_memories = []

        # daily_summaryの生成
        daily_summary = self.memory_generator.generate_daily_summary(current_day)
        if daily_summary:
            processed_memories.append(daily_summary)

        # 10日ごとのlevel_10生成
        if current_day > 0 and current_day % 10 == 0:
            level_10_memory = self.memory_generator.generate_hierarchical_summary(
                MEMORY_TYPE_LEVEL_10,
                start_day=max(1, current_day - 9),
                end_day=current_day,
            )
            if level_10_memory:
                processed_memories.append(level_10_memory)

        # 100日ごとのlevel_100生成
        if current_day > 0 and current_day % 100 == 0:
            level_100_memory = self.memory_generator.generate_hierarchical_summary(
                MEMORY_TYPE_LEVEL_100,
                start_day=max(1, current_day - 99),
                end_day=current_day,
            )
            if level_100_memory:
                processed_memories.append(level_100_memory)

        # 1000日ごとのlevel_1000生成
        if current_day > 0 and current_day % 1000 == 0:
            level_1000_memory = self.memory_generator.generate_hierarchical_summary(
                MEMORY_TYPE_LEVEL_1000,
                start_day=max(1, current_day - 999),
                end_day=current_day,
            )
            if level_1000_memory:
                processed_memories.append(level_1000_memory)

        # 長期archive記憶生成（複数のlevel_1000から）
        if current_day > 1000 and current_day % 1000 == 0:
            level_1000_memories = memory_crud.get_memories_by_character(
                db=self.db,
                character_id=self.character_id,
                memory_type=MEMORY_TYPE_LEVEL_1000,
            )

            if len(level_1000_memories) >= 2:
                min_start_day = min(mem.start_day for mem in level_1000_memories)
                max_end_day = max(mem.end_day for mem in level_1000_memories)

                level_archive_memory = (
                    self.memory_generator.generate_hierarchical_summary(
                        MEMORY_TYPE_LEVEL_ARCHIVE,
                        start_day=min_start_day,
                        end_day=max_end_day,
                    )
                )
                if level_archive_memory:
                    processed_memories.append(level_archive_memory)

        # 最終記憶処理日時を更新
        self.character.last_memory_processing_date = datetime.now()
        self.db.commit()

        return processed_memories

    def start_sleep_session(self, current_day: int) -> Dict[str, Any]:
        """
        睡眠セッションを開始し、記憶処理を実行する

        Args:
            current_day: 現在の日

        Returns:
            処理結果の要約
        """
        try:
            # 睡眠セッションを作成
            session = create_session(
                db=self.db,
                user_id=self.user_id,
                character_id=self.character_id,
                device_id="system",  # システム処理用のデバイスID
                session_type=SESSION_TYPE_SLEEP,
                properties={"current_day": current_day},
            )

            # 記憶処理を実行
            processed_memories = self.process_daily_memories(current_day)

            # セッションを完了状態に更新
            end_session(
                db=self.db,
                session_id=session.id,
                status=SESSION_STATUS_COMPLETED,
                properties={
                    "processed_memories_count": len(processed_memories),
                    "processed_memory_types": [
                        mem.memory_type for mem in processed_memories
                    ],
                    "processing_completed_at": datetime.now().isoformat(),
                },
            )

            return {
                "success": True,
                "character_id": str(self.character_id),
                "session_id": str(session.id),
                "processed_memories_count": len(processed_memories),
                "processed_memory_types": [
                    mem.memory_type for mem in processed_memories
                ],
                "processing_date": datetime.now().isoformat(),
            }
        except Exception as e:
            # エラーが発生した場合、セッションをエラー状態で終了
            if "session" in locals():
                end_session(
                    db=self.db,
                    session_id=session.id,
                    status=SESSION_STATUS_ERROR,
                    properties={"error": str(e)},
                )

            return {
                "success": False,
                "character_id": str(self.character_id),
                "error": str(e),
            }
