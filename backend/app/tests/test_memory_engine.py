import unittest
from unittest.mock import MagicMock, patch
import uuid
from datetime import datetime

from app.memory_engine.memory_generator import MemoryGenerator
from app.memory_engine.memory_retriever import MemoryRetriever
from app.memory_engine.sleep_processor import SleepProcessor
from app.core.constants.memory_types import (
    MEMORY_TYPE_DAILY_RAW, MEMORY_TYPE_DAILY_SUMMARY,
    MEMORY_TYPE_LEVEL_10, MEMORY_TYPE_LEVEL_100,
    MEMORY_TYPE_LEVEL_1000, MEMORY_TYPE_LEVEL_ARCHIVE
)

class TestMemoryEngine(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()
        self.character_id = uuid.uuid4()
        self.user_id = uuid.uuid4()
        
        self.mock_character = MagicMock()
        self.mock_character.id = self.character_id
        self.mock_character.user_id = self.user_id
        self.mock_character.is_sleeping = False
        self.mock_character.last_memory_processing_date = None
        
        self.mock_memory = MagicMock()
        self.mock_memory.id = uuid.uuid4()
        self.mock_memory.user_id = self.user_id
        self.mock_memory.character_id = self.character_id
        self.mock_memory.memory_type = MEMORY_TYPE_DAILY_RAW
        self.mock_memory.start_day = 1
        self.mock_memory.end_day = 1
        self.mock_memory.content = "テスト記憶内容"
        
        self.db.query.return_value.filter.return_value.first.return_value = self.mock_character
        
    @patch('app.memory_engine.memory_generator.memory_crud')
    @patch('app.memory_engine.memory_generator.completion')
    def test_memory_generator_convert_raw_conversation(self, mock_completion, mock_memory_crud):
        mock_completion.return_value.choices = [MagicMock(message=MagicMock(content="生成されたテスト記憶"))]
        
        mock_memory_crud.add_memory.return_value = self.mock_memory
        
        generator = MemoryGenerator(self.db, self.character_id)
        
        result = generator.convert_raw_conversation_to_daily_raw("テスト会話", 1)
        
        self.assertEqual(result, self.mock_memory)
        mock_completion.assert_called_once()
        mock_memory_crud.add_memory.assert_called_once()
    
    @patch('app.memory_engine.memory_generator.memory_crud')
    @patch('app.memory_engine.memory_generator.completion')
    def test_memory_generator_daily_summary(self, mock_completion, mock_memory_crud):
        mock_memory_crud.get_memories_by_character.return_value = [self.mock_memory]
        
        mock_completion.return_value.choices = [MagicMock(message=MagicMock(content="生成されたテスト要約"))]
        
        mock_memory_crud.add_memory.return_value = MagicMock(memory_type=MEMORY_TYPE_DAILY_SUMMARY)
        
        generator = MemoryGenerator(self.db, self.character_id)
        
        result = generator.generate_daily_summary(1)
        
        self.assertEqual(result.memory_type, MEMORY_TYPE_DAILY_SUMMARY)
        mock_completion.assert_called_once()
        mock_memory_crud.get_memories_by_character.assert_called_once()
        mock_memory_crud.add_memory.assert_called_once()
    
    @patch('app.memory_engine.memory_retriever.memory_crud')
    @patch('app.memory_engine.memory_retriever.completion')
    def test_memory_retriever_select_memories(self, mock_completion, mock_memory_crud):
        mock_memory1 = MagicMock(id=uuid.uuid4(), memory_type=MEMORY_TYPE_DAILY_SUMMARY)
        mock_memory2 = MagicMock(id=uuid.uuid4(), memory_type=MEMORY_TYPE_LEVEL_10)
        mock_memory_crud.get_memories_by_character.return_value = [mock_memory1, mock_memory2]
        
        mock_completion.return_value.choices = [
            MagicMock(message=MagicMock(content=f"Memory ID: {mock_memory1.id}"))
        ]
        
        retriever = MemoryRetriever(self.db, self.character_id)
        
        result = retriever.select_memories_for_session_context("テスト会話", 10)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], mock_memory1)
        mock_completion.assert_called_once()
        self.assertEqual(mock_memory_crud.get_memories_by_character.call_count, 5)  # 5つの記憶タイプに対して呼び出し
    
    @patch('app.memory_engine.sleep_processor.memory_crud')
    def test_sleep_processor_start_sleep_session(self, mock_memory_crud):
        mock_generator = MagicMock()
        mock_generator.generate_daily_summary.return_value = MagicMock(memory_type=MEMORY_TYPE_DAILY_SUMMARY)
        
        processor = SleepProcessor(self.db, self.character_id)
        processor.memory_generator = mock_generator
        
        result = processor.start_sleep_session(1)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["character_id"], str(self.character_id))
        self.assertEqual(result["processed_memories_count"], 1)
        self.assertEqual(result["processed_memory_types"], [MEMORY_TYPE_DAILY_SUMMARY])
        
        self.assertFalse(self.mock_character.is_sleeping)  # 処理後にFalseに戻る
        self.assertIsNotNone(self.mock_character.last_memory_processing_date)
        self.db.commit.assert_called()
        
        mock_generator.generate_daily_summary.assert_called_once_with(1)

if __name__ == '__main__':
    unittest.main()
