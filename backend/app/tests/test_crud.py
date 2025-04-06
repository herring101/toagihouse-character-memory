import pytest

from app.core.constants import MEMORY_TYPE_DAILY_RAW, SESSION_TYPE_CONVERSATION
from app.crud.character import (
    create_character,
    delete_character,
    get_character,
    get_characters_by_user,
    update_character,
)
from app.crud.memory import (
    add_memory,
    delete_memory,
    get_memories_by_character,
    update_memory,
)
from app.crud.session import create_session, end_session, get_active_session
from app.models import Session as DbSession


@pytest.mark.unit
class TestCharacterCRUD:
    def test_create_character(self, db_session, test_user_id):
        """キャラクター作成のテスト"""
        character = create_character(
            db=db_session,
            user_id=test_user_id,
            name="テストキャラクター",
            config={"test": True},
        )

        assert character is not None
        assert character.user_id == test_user_id
        assert character.name == "テストキャラクター"
        assert character.config == {"test": True}

    def test_get_character(self, db_session, test_character):
        """キャラクター取得のテスト"""
        character = get_character(db_session, test_character.id)

        assert character is not None
        assert character.id == test_character.id
        assert character.name == test_character.name

    def test_get_characters_by_user(self, db_session, test_user_id, test_character):
        """ユーザーのキャラクター一覧取得テスト"""
        characters = get_characters_by_user(db_session, test_user_id)

        assert len(characters) >= 1
        assert any(c.id == test_character.id for c in characters)

    def test_update_character(self, db_session, test_character):
        """キャラクター更新のテスト"""
        updated = update_character(
            db=db_session, character_id=test_character.id, name="更新されたキャラクター"
        )

        assert updated.name == "更新されたキャラクター"
        assert updated.id == test_character.id

    def test_delete_character(self, db_session, test_user_id):
        """キャラクター削除のテスト"""
        # テスト用の新しいキャラクターを作成
        character = create_character(
            db=db_session, user_id=test_user_id, name="削除用キャラクター"
        )

        # 削除
        result = delete_character(db_session, character.id)

        assert result is True

        # 削除後は取得できないことを確認
        deleted = get_character(db_session, character.id)
        assert deleted is None


@pytest.mark.unit
class TestMemoryCRUD:
    def test_add_memory(self, db_session, test_character):
        """記憶追加のテスト"""
        memory = add_memory(
            db=db_session,
            user_id=test_character.user_id,
            character_id=test_character.id,
            memory_type=MEMORY_TYPE_DAILY_RAW,
            start_day=1,
            end_day=1,
            content="テスト記憶内容",
        )

        assert memory is not None
        assert memory.character_id == test_character.id
        assert memory.memory_type == MEMORY_TYPE_DAILY_RAW
        assert memory.content == "テスト記憶内容"

    def test_get_memories_by_character(self, db_session, test_character, test_memory):
        """キャラクターの記憶取得テスト"""
        memories = get_memories_by_character(
            db=db_session, character_id=test_character.id
        )

        assert len(memories) >= 1
        assert any(m.id == test_memory.id for m in memories)

        # メモリタイプでフィルタリング
        filtered = get_memories_by_character(
            db=db_session,
            character_id=test_character.id,
            memory_type=MEMORY_TYPE_DAILY_RAW,
        )

        assert all(m.memory_type == MEMORY_TYPE_DAILY_RAW for m in filtered)

    def test_update_memory(self, db_session, test_memory):
        """記憶更新のテスト"""
        updated = update_memory(
            db=db_session, memory_id=test_memory.id, content="更新された記憶内容"
        )

        assert updated.content == "更新された記憶内容"
        assert updated.id == test_memory.id

    def test_delete_memory(self, db_session, test_character):
        """記憶削除のテスト"""
        # テスト用の新しい記憶を作成
        memory = add_memory(
            db=db_session,
            user_id=test_character.user_id,
            character_id=test_character.id,
            memory_type=MEMORY_TYPE_DAILY_RAW,
            start_day=2,
            end_day=2,
            content="削除用記憶内容",
        )

        # 削除
        result = delete_memory(db_session, memory.id)

        assert result is True


@pytest.mark.unit
class TestSessionCRUD:
    def test_create_session(self, db_session, test_user_id, test_character):
        """セッション作成のテスト"""
        session = create_session(
            db=db_session,
            user_id=test_user_id,
            character_id=test_character.id,
            device_id="test-device",
            session_type=SESSION_TYPE_CONVERSATION,
        )

        assert session is not None
        assert session.user_id == test_user_id
        assert session.character_id == test_character.id
        assert session.device_id == "test-device"
        assert session.is_active is True

    def test_get_active_session(self, db_session, test_user_id, test_character):
        """アクティブセッション取得のテスト"""
        # 既存のアクティブセッションを終了
        active_sessions = (
            db_session.query(DbSession)
            .filter(
                DbSession.character_id == test_character.id,
                DbSession.is_active.is_(True),
            )
            .all()
        )

        for session in active_sessions:
            end_session(db_session, session.id)

        # 新しいセッションを作成
        created = create_session(
            db=db_session,
            user_id=test_user_id,
            character_id=test_character.id,
            device_id="test-device",
            session_type=SESSION_TYPE_CONVERSATION,
        )

        # 取得
        active = get_active_session(db_session, test_character.id)

        assert active is not None
        assert active.id == created.id

    def test_end_session(self, db_session, test_user_id, test_character):
        """セッション終了のテスト"""
        # 既存のアクティブセッションを終了
        active_sessions = (
            db_session.query(DbSession)
            .filter(
                DbSession.character_id == test_character.id,
                DbSession.is_active.is_(True),
            )
            .all()
        )

        for session in active_sessions:
            end_session(db_session, session.id)

        # 新しいセッションを作成
        session = create_session(
            db=db_session,
            user_id=test_user_id,
            character_id=test_character.id,
            device_id="test-device",
            session_type=SESSION_TYPE_CONVERSATION,
        )

        # セッションを終了
        ended = end_session(db_session, session.id)

        assert ended.is_active is False

        # 確認
        active = get_active_session(db_session, test_character.id)
        assert active is None
