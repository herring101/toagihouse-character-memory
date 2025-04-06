import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# SQLiteの設定をインポート
from app.core.database import Base
from app.models import Character, Memory

# テスト用データベースの設定 - 常にSQLiteインメモリを使用
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_engine():
    """テスト用データベースエンジンを作成"""
    # SQLiteインメモリDBを使用 - 複数接続で同じメモリを共有
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # 単一のコネクションプールを使用
    )

    # テーブルスキーマを作成（このステップが重要）
    Base.metadata.create_all(bind=engine)

    yield engine


@pytest.fixture
def db_session(test_engine):
    """テスト関数ごとのデータベースセッション"""
    # テスト用のセッションファクトリを作成
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def test_user_id():
    """テスト用ユーザーID"""
    return uuid.uuid4()


@pytest.fixture
def test_character(db_session, test_user_id):
    """テスト用キャラクターを作成"""
    character = Character(
        user_id=test_user_id, name="テストキャラクター", config={"test": True}
    )
    db_session.add(character)
    db_session.commit()
    db_session.refresh(character)

    yield character

    # テスト後にロールバックでクリーンアップ（明示的な削除は不要）


@pytest.fixture
def test_memory(db_session, test_character):
    """テスト用記憶を作成"""
    memory = Memory(
        user_id=test_character.user_id,
        character_id=test_character.id,
        memory_type="daily_raw",
        start_day=1,
        end_day=1,
        content="テスト用記憶内容",
    )
    db_session.add(memory)
    db_session.commit()
    db_session.refresh(memory)

    yield memory


@pytest.fixture
def mock_llm_response(monkeypatch):
    """LiteLLMのモック応答を設定"""

    class MockResponse:
        class MockChoice:
            class MockMessage:
                def __init__(self, content):
                    self.content = content

            def __init__(self, content):
                self.message = self.MockMessage(content)

        def __init__(self, content):
            self.choices = [self.MockChoice(content)]

    def mock_completion(*args, **kwargs):
        return MockResponse("これはモックLLMの応答です。")

    # litellmのcompletionをモック化
    monkeypatch.setattr("litellm.completion", mock_completion)
