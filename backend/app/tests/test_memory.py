import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.core.constants import (
    MEMORY_TYPE_DAILY_RAW,
    MEMORY_TYPE_DAILY_SUMMARY,
    MEMORY_TYPE_LEVEL_10,
)
from app.memory.generator import MemoryGenerator
from app.memory.processor import SleepProcessor
from app.memory.retriever import MemoryRetriever


@pytest.mark.unit
class TestMemoryGenerator:
    def test_init_with_invalid_character(self, db_session):
        """無効なキャラクターIDでの初期化テスト"""
        with pytest.raises(ValueError):
            MemoryGenerator(db_session, uuid.uuid4())

    def test_convert_raw_conversation(
        self, db_session, test_character, mock_llm_response
    ):
        """生の会話からdaily_raw記憶への変換テスト"""
        generator = MemoryGenerator(db_session, test_character.id)

        # モックを使ってLLM呼び出しをパッチする
        with patch.object(
            generator, "_call_llm", return_value="これはモックLLMの応答です。"
        ):
            result = generator.convert_raw_conversation_to_daily_raw(
                conversation_history="ユーザー: こんにちは\nAI: こんにちは、元気ですか？",
                day=1,
            )

            assert result is not None
            assert result.memory_type == MEMORY_TYPE_DAILY_RAW
            assert result.start_day == 1
            assert result.end_day == 1
            assert result.content == "これはモックLLMの応答です。"

    def test_generate_daily_summary(
        self, db_session, test_character, mock_llm_response
    ):
        """daily_summary生成テスト"""
        # まずdaily_raw記憶を作成
        generator = MemoryGenerator(db_session, test_character.id)

        # _call_llmメソッドをモック化
        with patch.object(
            generator, "_call_llm", return_value="これはモックLLMの応答です。"
        ):
            # daily_raw記憶を生成
            generator.convert_raw_conversation_to_daily_raw(
                conversation_history="テスト会話", day=1
            )

            # daily_summaryを生成
            summary = generator.generate_daily_summary(1)

            assert summary is not None
            assert summary.memory_type == MEMORY_TYPE_DAILY_SUMMARY
            assert summary.start_day == 1
            assert summary.end_day == 1

    def test_generate_hierarchical_summary(
        self, db_session, test_character, mock_llm_response
    ):
        """階層的要約生成テスト"""
        # まず下位層の記憶を作成
        generator = MemoryGenerator(db_session, test_character.id)

        # _call_llmメソッドをモック化
        with patch.object(
            generator, "_call_llm", return_value="これはモックLLMの応答です。"
        ):
            # daily_summary複数個を作成
            for day in range(1, 11):
                generator.convert_raw_conversation_to_daily_raw(
                    conversation_history=f"テスト会話 - 日{day}", day=day
                )
                generator.generate_daily_summary(day)

            # level_10を生成
            level_10 = generator.generate_hierarchical_summary(
                memory_type=MEMORY_TYPE_LEVEL_10, start_day=1, end_day=10
            )

            assert level_10 is not None
            assert level_10.memory_type == MEMORY_TYPE_LEVEL_10
            assert level_10.start_day == 1
            assert level_10.end_day == 10
            assert level_10.content == "これはモックLLMの応答です。"


@pytest.mark.unit
class TestMemoryRetriever:
    def test_get_memories_for_session(self, db_session, test_character):
        """会話セッション用記憶取得テスト"""
        # いくつかの記憶を作成
        generator = MemoryGenerator(db_session, test_character.id, "dummy-model")

        with patch.object(generator, "_call_llm", return_value="テスト記憶内容"):
            # 1日目の記憶
            generator.convert_raw_conversation_to_daily_raw("テスト会話1", 1)
            generator.generate_daily_summary(1)

            # 2日目の記憶
            generator.convert_raw_conversation_to_daily_raw("テスト会話2", 2)
            generator.generate_daily_summary(2)

        # 記憶の取得テスト
        retriever = MemoryRetriever(db_session, test_character.id)
        memories = retriever.get_memories_for_session(current_day=2)

        assert "daily_summary" in memories
        assert len(memories["daily_summary"]) >= 2

    def test_format_memories_for_prompt(self, db_session, test_character):
        """プロンプト用記憶整形テスト"""
        # いくつかの記憶を作成
        generator = MemoryGenerator(db_session, test_character.id, "dummy-model")

        with patch.object(generator, "_call_llm", return_value="テスト記憶内容"):
            generator.convert_raw_conversation_to_daily_raw("テスト会話", 1)
            generator.generate_daily_summary(1)

        # 記憶の整形テスト
        retriever = MemoryRetriever(db_session, test_character.id)
        formatted = retriever.format_memories_for_prompt(current_day=1)

        assert "【記憶データ】" in formatted
        assert "テスト記憶内容" in formatted


@pytest.mark.unit
class TestSleepProcessor:
    def test_process_daily_memories(self, db_session, test_character):
        """睡眠中の記憶処理テスト"""
        # いくつかの記憶を作成
        generator = MemoryGenerator(db_session, test_character.id, "dummy-model")

        with patch.object(generator, "_call_llm", return_value="テスト記憶内容"):
            generator.convert_raw_conversation_to_daily_raw("テスト会話", 1)

        # 記憶処理のテスト
        processor = SleepProcessor(db_session, test_character.id, "dummy-model")

        with patch.object(
            processor.memory_generator, "_call_llm", return_value="処理された記憶内容"
        ):
            processed = processor.process_daily_memories(current_day=1)

        assert len(processed) >= 1
        assert processed[0].memory_type == MEMORY_TYPE_DAILY_SUMMARY

    @patch("app.memory.processor.create_session")
    @patch("app.memory.processor.end_session")
    def test_start_sleep_session(
        self, mock_end_session, mock_create_session, db_session, test_character
    ):
        """睡眠セッション開始テスト"""
        # モックセッションの設定
        mock_session = MagicMock()
        mock_session.id = uuid.uuid4()
        mock_create_session.return_value = mock_session

        # 睡眠プロセッサの作成
        processor = SleepProcessor(db_session, test_character.id, "dummy-model")

        # process_daily_memoriesをモック化
        with patch.object(
            processor,
            "process_daily_memories",
            return_value=[MagicMock(memory_type=MEMORY_TYPE_DAILY_SUMMARY)],
        ):
            result = processor.start_sleep_session(current_day=1)

        assert result["success"] is True
        assert result["character_id"] == str(test_character.id)
        assert result["processed_memories_count"] == 1
        assert mock_create_session.called
        assert mock_end_session.called
