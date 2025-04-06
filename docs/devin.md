# ToagiHouse Character Memory System - Supabase接続設定ガイド

## 現在の環境状態

現在の環境では以下の状態が確認されています：

- **環境変数**: `SUPABASE_DB_PASSWORD`は設定済み
- **Supabase接続**: ローカルのPostgreSQLサーバー（ポート54322）は現在実行されていません
- **必要なパッケージ**: フロントエンド・バックエンド共にSupabase関連パッケージは未インストール

## タスク1.2「データアクセス関数の実装」に向けた準備

### 1. 必要なパッケージのインストール

#### フロントエンド (Next.js)

```bash
cd ~/repos/toagihouse-character-memory/chat-app
npm install @supabase/supabase-js
```

#### バックエンド (FastAPI)

```bash
cd ~/repos/toagihouse-character-memory/backend
source venv/bin/activate
pip install psycopg2-binary sqlalchemy supabase
```

### 2. Supabase接続の設定

#### フロントエンド用Supabaseクライアント

`chat-app/src/lib/supabase.ts`を作成します：

```typescript
import { createClient } from '@supabase/supabase-js';

// 環境変数から接続情報を取得
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

// Supabaseクライアントの作成
export const supabase = createClient(supabaseUrl, supabaseAnonKey);
```

#### バックエンド用データベース接続

`backend/database.py`を作成します：

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 環境変数のロード
load_dotenv()

# データベース接続URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # ローカル開発用のデフォルト接続文字列
    SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")
    DATABASE_URL = f"postgresql://postgres:{SUPABASE_DB_PASSWORD}@localhost:54322/postgres"

# SQLAlchemy設定
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# DBセッションの依存関係
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 3. データモデルの定義

`backend/models.py`を作成して、データベーススキーマに対応するモデルを定義します：

```python
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Text, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from database import Base

class Character(Base):
    __tablename__ = "characters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    config = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Memory(Base):
    __tablename__ = "memories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    memory_type = Column(String, nullable=False)
    start_day = Column(Integer, nullable=False)
    end_day = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    character_id = Column(UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False)
    device_id = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

## タスク1.2「データアクセス関数の実装」の実装ステップ

1. **キャラクター管理関数の実装**:
   - キャラクター作成関数: `create_character(user_id, name, config={})`
   - キャラクター取得関数: `get_character(character_id)`, `get_characters_by_user(user_id)`
   - キャラクター更新関数: `update_character(character_id, name=None, config=None)`
   - キャラクター削除関数: `delete_character(character_id)`

2. **記憶管理関数の実装**:
   - 記憶追加関数: `add_memory(user_id, character_id, memory_type, start_day, end_day, content)`
   - 記憶検索・取得関数: `get_memories_by_character(character_id, memory_type=None, start_day=None, end_day=None)`
   - 記憶更新関数: `update_memory(memory_id, content=None, memory_type=None)`
   - 記憶削除関数: `delete_memory(memory_id)`

3. **セッション管理関数の実装**:
   - セッション作成関数: `create_session(user_id, character_id, device_id)`
   - セッション取得関数: `get_active_session(character_id, device_id)`
   - セッション更新関数: `update_session(session_id, is_active=None)`
   - セッション終了関数: `end_session(session_id)`

## 実装の進捗

### タスク1.2「データアクセス関数の実装」の完了

以下のデータアクセス関数が実装されました：

1. **キャラクター管理関数**
   - `create_character`: 新しいキャラクターを作成する関数
   - `get_character`: キャラクターIDでキャラクターを取得する関数
   - `get_characters_by_user`: ユーザーIDに基づいてキャラクターのリストを取得する関数
   - `update_character`: キャラクター情報を更新する関数
   - `delete_character`: キャラクターを削除する関数

2. **記憶管理関数**
   - `add_memory`: 新しい記憶を追加する関数
   - `get_memories_by_character`: キャラクターIDと条件に基づいて記憶を取得する関数
   - `update_memory`: 記憶の内容や種類を更新する関数
   - `delete_memory`: 記憶を削除する関数

3. **セッション管理関数**
   - `create_session`: 新しいセッションを作成する関数
   - `get_active_session`: キャラクターIDとデバイスIDに基づいてアクティブなセッションを取得する関数
   - `update_session`: セッション情報を更新する関数
   - `end_session`: セッションを終了する関数

### 実装中に遭遇した問題と解決策

1. **データベース接続の問題**
   - **問題**: 初期実装ではローカルのPostgreSQLサーバー（localhost:54322）への接続を試みていましたが、実際にはリモートのSupabaseサーバーを使用する必要がありました。
   - **解決策**: `database.py`を修正し、`SUPABASE_URL`環境変数からホスト名を抽出して正しい接続文字列を構築するようにしました。
   ```python
   host_match = re.search(r'https://([^.]+)\.supabase\.co', SUPABASE_URL)
   if host_match:
       host_id = host_match.group(1)
       DATABASE_URL = f"postgresql://postgres:{SUPABASE_DB_PASSWORD}@db.{host_id}.supabase.co:5432/postgres"
   ```

2. **リンター警告**
   - **問題**: ruffリンターによって未使用のインポートや不適切なブール比較などの警告が検出されました。
   - **解決策**: 未使用のインポートを削除し、`is_active == True`のような比較を`is_active`に簡略化しました。

3. **dotenv依存関係の削除**
   - **問題**: 初期実装ではpython-dotenvを使用して.envファイルから環境変数を読み込んでいましたが、環境変数を直接使用する方が望ましいとの要件がありました。
   - **解決策**: `database.py`と`test_data_access.py`からdotenv依存関係を削除し、`os.environ.get()`を使用して直接環境変数を取得するように変更しました。

4. **Supabaseへの直接接続の制限**
   - **問題**: Supabaseデータベースへの直接PostgreSQL接続（ポート5432）が「Network is unreachable」エラーで失敗しました。これはSupabaseのセキュリティ設定によるものと思われます。
   - **解決策**: 実際の運用環境では、Supabase REST APIを使用するか、ローカル開発環境でSupabase CLIを使用してローカルのPostgreSQLサーバーを起動する必要があります。テスト環境では、モックを使用したユニットテストを実装しました。

### 次のステップ

タスク1.3「追加マイグレーションとRLS設定」または、Phase 2「記憶管理エンジン」の実装に進みます。

## 開発時の注意点

1. **Supabase接続**:
   - 現在の環境では、ローカルのPostgreSQLサーバーは実行されていません
   - 実際の開発では、Supabase CLIを使用するか、リモートのSupabaseプロジェクトに接続する必要があります

2. **環境変数**:
   - `SUPABASE_URL`と`SUPABASE_ANON_KEY`の設定が必要です
   - リモートSupabaseプロジェクトに接続する場合は、`DATABASE_URL`の設定も必要です

3. **Row Level Security (RLS)**:
   - データベーススキーマには既にRLSポリシーが設定されています
   - データアクセス関数の実装時には、これらのポリシーを考慮する必要があります

4. **テスト方法**:
   - 実装したデータアクセス関数は、単体テストを作成して検証することをお勧めします
   - Supabaseのローカル開発環境を使用する場合は、`supabase start`コマンドでサーバーを起動できます
   - バックエンドのテスト方法は以下の通りです：

### バックエンドのテスト方法

#### 1. ユニットテストの実行

モックを使用したユニットテストは以下のコマンドで実行できます：

```bash
cd ~/repos/toagihouse-character-memory/backend
source venv/bin/activate
python -m unittest tests/test_crud.py
```

このテストはデータベース接続をモック化しているため、実際のデータベース接続は必要ありません。

#### 2. 統合テストの実行

実際のデータベースを使用したテストを行う場合は、以下の環境変数を設定してから`test_data_access.py`を実行します：

```bash
cd ~/repos/toagihouse-character-memory/backend
source venv/bin/activate
export SUPABASE_URL="https://kquspjkyrlvwywkfrczu.supabase.co"
export SUPABASE_DB_PASSWORD="your_password_here"
python test_data_access.py
```

注意: Supabaseへの直接PostgreSQL接続はネットワーク制限により失敗する可能性があります。その場合は、ローカル開発環境でSupabase CLIを使用するか、Supabase REST APIを使用してテストを行ってください。

#### 3. モックを使用したテスト作成方法

新しいテストを作成する場合は、`tests/test_crud.py`を参考にしてください。基本的な手順は以下の通りです：

1. `unittest.mock.MagicMock`を使用してデータベースセッションをモック化
2. 必要なメソッド（`query`, `filter`, `first`など）の戻り値を設定
3. テスト対象の関数を呼び出し
4. モックが期待通りに呼び出されたことを検証

例：
```python
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
```
