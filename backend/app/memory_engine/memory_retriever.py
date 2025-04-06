from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import uuid

from app.models import Memory, Character
from app.crud import memory as memory_crud
from app.core.constants.memory_types import (
    MEMORY_TYPE_DAILY_SUMMARY, MEMORY_TYPE_LEVEL_10, 
    MEMORY_TYPE_LEVEL_100, MEMORY_TYPE_LEVEL_1000, 
    MEMORY_TYPE_LEVEL_ARCHIVE
)
from app.core.prompts.memory_prompts import SESSION_CONTEXT_PROMPT
from litellm import completion

class MemoryRetriever:
    def __init__(self, db: Session, character_id: uuid.UUID, model: str = "gemini/gemini-2.0-flash"):
        """
        記憶取得エンジンの初期化
        
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
            
    def select_memories_for_session_context(self, current_conversation: str, current_day: int, max_memories: int = 10) -> List[Memory]:
        """
        現在のセッションコンテキストに関連する記憶を選択する
        
        Args:
            current_conversation: 現在の会話
            current_day: 現在の日
            max_memories: 選択する記憶の最大数
            
        Returns:
            選択された記憶のリスト
        """
        all_memories = []
        
        for memory_type in [MEMORY_TYPE_DAILY_SUMMARY, MEMORY_TYPE_LEVEL_10, MEMORY_TYPE_LEVEL_100, MEMORY_TYPE_LEVEL_1000, MEMORY_TYPE_LEVEL_ARCHIVE]:
            memories = memory_crud.get_memories_by_character(
                db=self.db,
                character_id=self.character_id,
                memory_type=memory_type,
                end_day=current_day,
                limit=max_memories
            )
            all_memories.extend(memories)
        
        if not all_memories:
            return []
            
        memories_str = "\n\n".join([
            f"Memory ID: {mem.id}\nType: {mem.memory_type}\nDays: {mem.start_day}-{mem.end_day}\nContent: {mem.content}" 
            for mem in all_memories
        ])
        
        prompt = SESSION_CONTEXT_PROMPT.format(
            current_conversation=current_conversation,
            available_memories=memories_str,
            max_memories=max_memories
        )
        
        response = self._call_llm(prompt)
        
        selected_ids = []
        for line in response.split('\n'):
            if "Memory ID:" in line:
                try:
                    memory_id = line.split("Memory ID:")[1].strip()
                    selected_ids.append(uuid.UUID(memory_id))
                except (IndexError, ValueError):
                    continue
        
        return [mem for mem in all_memories if mem.id in selected_ids]
