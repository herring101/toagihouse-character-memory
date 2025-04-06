from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional, Union
import uuid
import os
import time
import json
from datetime import datetime, timedelta

from app.models import Memory, Character
from app.crud import memory as memory_crud
from app.core.constants.memory_types import (
    MEMORY_TYPE_DAILY_RAW, MEMORY_TYPE_DAILY_SUMMARY,
    MEMORY_TYPE_LEVEL_10, MEMORY_TYPE_LEVEL_100,
    MEMORY_TYPE_LEVEL_1000, MEMORY_TYPE_LEVEL_ARCHIVE,
    MEMORY_HIERARCHY
)
from app.core.prompts.memory_prompts import (
    DAILY_RAW_CONVERSION_PROMPT, DAILY_SUMMARY_PROMPT,
    HIERARCHICAL_SUMMARY_PROMPT
)
from litellm import completion

class MemoryGenerator:
    def __init__(self, db: Session, character_id: uuid.UUID, model: str = "gemini/gemini-2.0-flash"):
        """
        記憶生成エンジンの初期化
        
        Args:
            db: データベースセッション
            character_id: キャラクターID
            model: 使用するLLMモデル
        """
        self.db = db
        self.character_id = character_id
        self.model = model
        self.character = db.query(Character).filter(Character.id == character_id).first()
        if not self.character:
            raise ValueError(f"キャラクターID {character_id} が見つかりません")
        self.user_id = self.character.user_id
        
    def _call_llm(self, prompt: str, messages: Optional[List[Dict[str, str]]] = None) -> str:
        """
        LLMを呼び出して応答を取得する
        
        Args:
            prompt: プロンプト文字列
            messages: メッセージリスト（プロンプトがNoneの場合に使用）
            
        Returns:
            LLMの応答テキスト
        """
        try:
            if messages is None:
                messages = [{"role": "user", "content": prompt}]
                
            response = completion(model=self.model, messages=messages, stream=False)
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM呼び出し中にエラーが発生しました: {str(e)}")
            return ""
            
    def convert_raw_conversation_to_daily_raw(self, conversation_history: str, day: int) -> Optional[Memory]:
        """
        生の会話をdaily_raw記憶に変換する
        
        Args:
            conversation_history: 会話履歴
            day: 記憶が関連する日
            
        Returns:
            生成された記憶オブジェクト
        """
        prompt = DAILY_RAW_CONVERSION_PROMPT.format(conversation_history=conversation_history)
        memory_content = self._call_llm(prompt)
        
        if not memory_content:
            return None
            
        return memory_crud.add_memory(
            db=self.db,
            user_id=self.user_id,
            character_id=self.character_id,
            memory_type=MEMORY_TYPE_DAILY_RAW,
            start_day=day,
            end_day=day,
            content=memory_content
        )
        
    def generate_daily_summary(self, day: int) -> Optional[Memory]:
        """
        特定の日のdaily_raw記憶からdaily_summaryを生成する
        
        Args:
            day: 記憶が関連する日
            
        Returns:
            生成されたdaily_summary記憶オブジェクト
        """
        raw_memories = memory_crud.get_memories_by_character(
            db=self.db,
            character_id=self.character_id,
            memory_type=MEMORY_TYPE_DAILY_RAW,
            start_day=day,
            end_day=day
        )
        
        if not raw_memories:
            return None
            
        combined_raw = "\n\n".join([mem.content for mem in raw_memories])
        
        prompt = DAILY_SUMMARY_PROMPT.format(daily_raw_memory=combined_raw)
        summary_content = self._call_llm(prompt)
        
        if not summary_content:
            return None
            
        return memory_crud.add_memory(
            db=self.db,
            user_id=self.user_id,
            character_id=self.character_id,
            memory_type=MEMORY_TYPE_DAILY_SUMMARY,
            start_day=day,
            end_day=day,
            content=summary_content
        )
        
    def generate_hierarchical_summary(self, memory_type: str, start_day: int, end_day: int) -> Optional[Memory]:
        """
        より低レベルの記憶から階層的な要約を生成する
        
        Args:
            memory_type: 生成する記憶タイプ（level_10, level_100, level_1000, level_archive）
            start_day: 開始日
            end_day: 終了日
            
        Returns:
            生成された階層的要約記憶オブジェクト
        """
        hierarchy_level = MEMORY_HIERARCHY.get(memory_type)
        if hierarchy_level is None or hierarchy_level <= 1:
            raise ValueError(f"無効な記憶タイプです: {memory_type}")
            
        input_memory_type = None
        for mem_type, level in MEMORY_HIERARCHY.items():
            if level == hierarchy_level - 1:
                input_memory_type = mem_type
                break
                
        if not input_memory_type:
            raise ValueError(f"記憶タイプ {memory_type} の入力記憶タイプが見つかりません")
            
        input_memories = memory_crud.get_memories_by_character(
            db=self.db,
            character_id=self.character_id,
            memory_type=input_memory_type,
            start_day=start_day,
            end_day=end_day
        )
        
        if not input_memories:
            return None
            
        combined_input = "\n\n".join([
            f"Day {mem.start_day}-{mem.end_day}: {mem.content}" 
            for mem in input_memories
        ])
        
        prompt = HIERARCHICAL_SUMMARY_PROMPT.format(input_memories=combined_input)
        summary_content = self._call_llm(prompt)
        
        if not summary_content:
            return None
            
        return memory_crud.add_memory(
            db=self.db,
            user_id=self.user_id,
            character_id=self.character_id,
            memory_type=memory_type,
            start_day=start_day,
            end_day=end_day,
            content=summary_content
        )
