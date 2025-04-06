import uuid
from typing import Dict, List, Tuple

from sqlalchemy.orm import Session

from app.core.constants import (
    MEMORY_TYPE_DAILY_RAW,
    MEMORY_TYPE_DAILY_SUMMARY,
    MEMORY_TYPE_LEVEL_10,
    MEMORY_TYPE_LEVEL_100,
    MEMORY_TYPE_LEVEL_1000,
    MEMORY_TYPE_LEVEL_ARCHIVE,
)
from app.crud import memory as memory_crud
from app.models import Character, Memory


class MemoryRetriever:
    """記憶取得エンジン

    会話や睡眠セッションに必要な記憶を階層構造に従って取得する。
    """

    def __init__(self, db: Session, character_id: uuid.UUID):
        """
        記憶取得エンジンの初期化

        Args:
            db: データベースセッション
            character_id: キャラクターID
        """
        self.db = db
        self.character_id = character_id
        self.character = (
            db.query(Character).filter(Character.id == character_id).first()
        )
        if not self.character:
            raise ValueError(f"キャラクターID {character_id} が見つかりません")
        self.user_id = self.character.user_id

    def get_memories_for_session(self, current_day: int) -> Dict[str, List[Memory]]:
        """
        会話セッションに必要な記憶を階層パターンに従って取得する

        Args:
            current_day: 現在の日

        Returns:
            階層別の記憶のディクショナリ
        """
        memories = {
            "daily_raw": [],
            "daily_summary": [],
            "level_10": [],
            "level_100": [],
            "level_1000": [],
            "level_archive": [],
        }

        # その日のdaily_raw（あれば）
        daily_raw = memory_crud.get_memories_by_character(
            db=self.db,
            character_id=self.character_id,
            memory_type=MEMORY_TYPE_DAILY_RAW,
            start_day=current_day,
            end_day=current_day,
        )
        memories["daily_raw"].extend(daily_raw)

        # 直近10日分のdaily_summary
        for day in range(max(1, current_day - 9), current_day + 1):
            summaries = memory_crud.get_memories_by_character(
                db=self.db,
                character_id=self.character_id,
                memory_type=MEMORY_TYPE_DAILY_SUMMARY,
                start_day=day,
                end_day=day,
            )
            memories["daily_summary"].extend(summaries)

        # 11-100日前の10日単位level_10
        for start_day in range(max(1, current_day - 100), current_day - 9, 10):
            end_day = min(start_day + 9, current_day - 10)
            if start_day > end_day:
                continue

            level_10s = memory_crud.get_memories_by_character(
                db=self.db,
                character_id=self.character_id,
                memory_type=MEMORY_TYPE_LEVEL_10,
                start_day=start_day,
                end_day=end_day,
            )
            memories["level_10"].extend(level_10s)

        # 101-1000日前の100日単位level_100
        for start_day in range(max(1, current_day - 1000), current_day - 100, 100):
            end_day = min(start_day + 99, current_day - 101)
            if start_day > end_day:
                continue

            level_100s = memory_crud.get_memories_by_character(
                db=self.db,
                character_id=self.character_id,
                memory_type=MEMORY_TYPE_LEVEL_100,
                start_day=start_day,
                end_day=end_day,
            )
            memories["level_100"].extend(level_100s)

        # 1001日以降の1000日単位level_1000と長期archive
        if current_day > 1000:
            # 1001-10000日前のlevel_1000
            for start_day in range(
                max(1, current_day - 10000), current_day - 1000, 1000
            ):
                end_day = min(start_day + 999, current_day - 1001)
                if start_day > end_day:
                    continue

                level_1000s = memory_crud.get_memories_by_character(
                    db=self.db,
                    character_id=self.character_id,
                    memory_type=MEMORY_TYPE_LEVEL_1000,
                    start_day=start_day,
                    end_day=end_day,
                )
                memories["level_1000"].extend(level_1000s)

            # 10001日以降のlevel_archive
            if current_day > 10000:
                archives = memory_crud.get_memories_by_character(
                    db=self.db,
                    character_id=self.character_id,
                    memory_type=MEMORY_TYPE_LEVEL_ARCHIVE,
                    end_day=current_day - 10001,
                )
                memories["level_archive"].extend(archives)

        return memories

    def get_memories_for_system_prompt(
        self, current_day: int
    ) -> List[Tuple[str, Memory]]:
        """
        システムプロンプト用に整理された記憶のリストを取得する

        Args:
            current_day: 現在の日

        Returns:
            (記憶タイプのラベル, 記憶オブジェクト)のタプルのリスト
        """
        memories_dict = self.get_memories_for_session(current_day)

        # 整理されたタプルのリストを作成
        memory_tuples = []

        # daily_rawの追加
        for memory in memories_dict["daily_raw"]:
            memory_tuples.append(("今日の記録", memory))

        # daily_summaryの追加
        for memory in memories_dict["daily_summary"]:
            days_ago = current_day - memory.start_day
            if days_ago == 0:
                label = "今日の記憶"
            elif days_ago == 1:
                label = "昨日の記憶"
            else:
                label = f"{days_ago}日前の記憶"
            memory_tuples.append((label, memory))

        # level_10の追加
        for memory in memories_dict["level_10"]:
            start_days_ago = current_day - memory.start_day
            end_days_ago = current_day - memory.end_day
            label = f"{end_days_ago}〜{start_days_ago}日前の記憶"
            memory_tuples.append((label, memory))

        # level_100の追加
        for memory in memories_dict["level_100"]:
            start_days_ago = current_day - memory.start_day
            end_days_ago = current_day - memory.end_day
            label = f"{end_days_ago}〜{start_days_ago}日前の記憶"
            memory_tuples.append((label, memory))

        # level_1000の追加
        for memory in memories_dict["level_1000"]:
            start_days_ago = current_day - memory.start_day
            end_days_ago = current_day - memory.end_day
            label = f"{end_days_ago}〜{start_days_ago}日前の記憶"
            memory_tuples.append((label, memory))

        # level_archiveの追加
        for memory in memories_dict["level_archive"]:
            days_ago = current_day - memory.end_day
            label = f"{days_ago}日以前の記憶"
            memory_tuples.append((label, memory))

        # 日付順にソート（最新から最古へ）
        memory_tuples.sort(key=lambda x: x[1].start_day, reverse=True)

        return memory_tuples

    def format_memories_for_prompt(self, current_day: int) -> str:
        """
        システムプロンプト用に記憶を整形する

        Args:
            current_day: 現在の日

        Returns:
            プロンプト用に整形された記憶テキスト
        """
        memory_tuples = self.get_memories_for_system_prompt(current_day)

        if not memory_tuples:
            return "記憶データはありません。"

        # 整形されたテキストを作成
        formatted_text = "【記憶データ】\n"

        for label, memory in memory_tuples:
            formatted_text += f"--- {label} ---\n{memory.content}\n\n"

        return formatted_text
