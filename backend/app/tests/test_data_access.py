import os
import sys
import uuid
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.crud as crud

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_DB_PASSWORD = os.environ.get("SUPABASE_DB_PASSWORD")

print(f"テスト用Supabase URL: {SUPABASE_URL}")
print(f"パスワード設定状況: {'設定済み' if SUPABASE_DB_PASSWORD else '未設定'}")

if SUPABASE_URL and SUPABASE_DB_PASSWORD:
    host_match = re.search(r'https://([^.]+)\.supabase\.co', SUPABASE_URL)
    if host_match:
        host_id = host_match.group(1)
        DATABASE_URL = f"postgresql://postgres:{SUPABASE_DB_PASSWORD}@db.{host_id}.supabase.co:5432/postgres"
        print(f"テスト用接続先: db.{host_id}.supabase.co:5432")
    else:
        DATABASE_URL = f"postgresql://postgres:{SUPABASE_DB_PASSWORD}@localhost:54322/postgres"
        print("テスト用接続先: localhost:54322")
else:
    DATABASE_URL = os.environ.get("DATABASE_URL")
    print(f"テスト用DATABASE_URL環境変数を使用: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_character_crud():
    """キャラクターCRUD操作のテスト"""
    db = SessionLocal()
    try:
        user_id = uuid.uuid4()
        
        print("=== キャラクターCRUDテスト開始 ===")
        
        print("キャラクター作成中...")
        character = crud.create_character(db, user_id, "テストキャラクター", {"description": "テスト用キャラクター"})
        print(f"作成されたキャラクター: ID={character.id}, 名前={character.name}")
        
        print("キャラクター取得中...")
        retrieved_character = crud.get_character(db, character.id)
        print(f"取得されたキャラクター: ID={retrieved_character.id}, 名前={retrieved_character.name}")
        
        print("キャラクター更新中...")
        updated_character = crud.update_character(db, character.id, name="更新されたキャラクター")
        print(f"更新されたキャラクター: ID={updated_character.id}, 名前={updated_character.name}")
        
        print("キャラクター削除中...")
        result = crud.delete_character(db, character.id)
        print(f"削除結果: {result}")
        
        print("=== キャラクターCRUDテスト完了 ===")
        return True
    except Exception as e:
        print(f"エラー発生: {str(e)}")
        return False
    finally:
        db.close()

def test_memory_crud():
    """記憶CRUD操作のテスト"""
    db = SessionLocal()
    try:
        user_id = uuid.uuid4()
        character = crud.create_character(db, user_id, "記憶テスト用キャラクター")
        
        print("=== 記憶CRUDテスト開始 ===")
        
        print("記憶追加中...")
        memory = crud.add_memory(
            db, user_id, character.id, "daily_raw", 
            start_day=1, end_day=1, 
            content="これはテスト用の記憶です。"
        )
        print(f"追加された記憶: ID={memory.id}, タイプ={memory.memory_type}")
        
        print("記憶取得中...")
        memories = crud.get_memories_by_character(db, character.id)
        print(f"取得された記憶数: {len(memories)}")
        
        print("記憶更新中...")
        updated_memory = crud.update_memory(db, memory.id, content="これは更新された記憶です。")
        print(f"更新された記憶: ID={updated_memory.id}, 内容={updated_memory.content[:20]}...")
        
        print("記憶削除中...")
        result = crud.delete_memory(db, memory.id)
        print(f"削除結果: {result}")
        
        crud.delete_character(db, character.id)
        
        print("=== 記憶CRUDテスト完了 ===")
        return True
    except Exception as e:
        print(f"エラー発生: {str(e)}")
        return False
    finally:
        db.close()

def test_session_crud():
    """セッションCRUD操作のテスト"""
    db = SessionLocal()
    try:
        user_id = uuid.uuid4()
        character = crud.create_character(db, user_id, "セッションテスト用キャラクター")
        device_id = "test-device-001"
        
        print("=== セッションCRUDテスト開始 ===")
        
        print("セッション作成中...")
        session = crud.create_session(db, user_id, character.id, device_id)
        print(f"作成されたセッション: ID={session.id}, アクティブ={session.is_active}")
        
        print("アクティブセッション取得中...")
        active_session = crud.get_active_session(db, character.id, device_id)
        print(f"取得されたアクティブセッション: ID={active_session.id if active_session else 'なし'}")
        
        print("セッション更新中...")
        updated_session = crud.update_session(db, session.id, is_active=True)
        print(f"更新されたセッション: ID={updated_session.id}, アクティブ={updated_session.is_active}")
        
        print("セッション終了中...")
        ended_session = crud.end_session(db, session.id)
        print(f"終了されたセッション: ID={ended_session.id}, アクティブ={ended_session.is_active}")
        
        crud.delete_character(db, character.id)
        
        print("=== セッションCRUDテスト完了 ===")
        return True
    except Exception as e:
        print(f"エラー発生: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("データアクセス関数のテストを開始します...")
    
    character_test = test_character_crud()
    memory_test = test_memory_crud()
    session_test = test_session_crud()
    
    print("\n=== テスト結果サマリー ===")
    print(f"キャラクターCRUDテスト: {'成功' if character_test else '失敗'}")
    print(f"記憶CRUDテスト: {'成功' if memory_test else '失敗'}")
    print(f"セッションCRUDテスト: {'成功' if session_test else '失敗'}")
    
    if character_test and memory_test and session_test:
        print("\n全てのテストが成功しました！")
        sys.exit(0)
    else:
        print("\nいくつかのテストが失敗しました。")
        sys.exit(1)
