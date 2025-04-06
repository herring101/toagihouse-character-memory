import unittest
from unittest.mock import MagicMock
import uuid

from app.models import Character
from app.crud.character import create_character, get_character

class TestCharacterCRUD(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()
        self.user_id = uuid.uuid4()
        self.character_id = uuid.uuid4()
        
    def test_create_character(self):
        self.db.add = MagicMock()
        self.db.commit = MagicMock()
        self.db.refresh = MagicMock()
        
        create_character(self.db, self.user_id, "テストキャラクター")
        
        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once()
    
    def test_get_character(self):
        query_mock = MagicMock()
        filter_mock = MagicMock()
        
        self.db.query.return_value = query_mock
        query_mock.filter.return_value = filter_mock
        filter_mock.first.return_value = Character(id=self.character_id, user_id=self.user_id, name="テスト")
        
        result = get_character(self.db, self.character_id)
        
        self.db.query.assert_called_once_with(Character)
        query_mock.filter.assert_called_once()
        self.assertEqual(result.id, self.character_id)


if __name__ == "__main__":
    unittest.main()
