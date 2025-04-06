# ToagiHouse Character Memory System - 開発ガイド

## よく使うコマンド

### 環境セットアップ

```bash
# 初期セットアップ
./setup.sh

# アプリケーション起動
./start-app.sh
```

### バックエンド開発

```bash
# 仮想環境の有効化
cd ~/repos/toagihouse-character-memory/backend
source venv/bin/activate

# バックエンドサーバー起動
python run.py

# リンターの実行
ruff check .

# ユニットテスト実行
python -m unittest app/tests/test_crud.py

# 統合テスト実行
python app/tests/test_data_access.py
```

### フロントエンド開発

```bash
# 依存関係のインストール
cd ~/repos/toagihouse-character-memory/chat-app
npm install

# 開発サーバー起動
npm run dev

# リンターの実行
npm run lint
```

## プロジェクト構造

### バックエンド構造

```
backend/
├── app/                    # アプリケーションコード
│   ├── api/                # API関連のコード
│   ├── core/               # コア機能（データベース接続など）
│   │   └── database.py     # データベース接続設定
│   ├── crud/               # データアクセス関数
│   │   ├── character.py    # キャラクター管理関数
│   │   ├── memory.py       # 記憶管理関数
│   │   └── session.py      # セッション管理関数
│   ├── models/             # データモデル
│   │   └── __init__.py     # SQLAlchemyモデル定義
│   ├── tests/              # テストコード
│   └── main.py             # FastAPIアプリケーション
├── run.py                  # アプリケーション起動スクリプト
└── requirements.txt        # 依存パッケージリスト
```

### フロントエンド構造

```
chat-app/
├── public/                 # 静的ファイル
├── src/                    # ソースコード
│   ├── app/                # Next.jsアプリケーション
│   │   ├── api/            # APIルート
│   │   └── page.tsx        # メインページ
│   ├── components/         # Reactコンポーネント
│   │   └── chat/           # チャット関連コンポーネント
│   └── lib/                # ユーティリティ
│       └── supabase.ts     # Supabaseクライアント
└── package.json            # 依存関係定義
```

## 実装の進捗

### 完了したタスク

- ✅ **Phase 1.1**: Supabase接続設定
- ✅ **Phase 1.2**: データアクセス関数の実装
  - キャラクター管理CRUD操作
  - 記憶管理CRUD操作
  - セッション管理CRUD操作

### 次のタスク

- ✅ **Phase 1.3**: 追加マイグレーションとRLS設定
  - キャラクターテーブルに睡眠状態と記憶処理日時の追加
  - 記憶テーブルに処理状態フラグの追加
  - 記憶取得の最適化のためのインデックス追加
- ✅ **Phase 2**: 記憶管理エンジンの実装
  - 記憶構造の設計と定数定義
  - 記憶生成プロセスの実装
  - 記憶取得プロセスの実装
  - 睡眠時の記憶処理メカニズムの実装

### 次のタスク

- **Phase 3**: APIレイヤーの実装
- **Phase 4**: ユーザーインターフェースの実装

## 注意点と解決済みの問題

### 環境変数

- ✅ **dotenv依存関係の削除**: 環境変数は`os.environ.get()`で直接取得するように変更
- ⚠️ **必要な環境変数**:
  - LLM API: `OPENAI_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`（少なくとも1つ）
  - Supabase: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_DB_PASSWORD`

### データベース接続

- ⚠️ **Supabaseへの直接接続制限**: Supabaseデータベースへの直接PostgreSQL接続（ポート5432）は失敗するため、ローカル接続（ポート54322）を使用するように設定を変更しました
- ✅ **解決策**: ローカル開発環境では`localhost:54322`への接続を優先します。必要に応じて`app/core/database.py`と`app/tests/test_data_access.py`のコメントを編集することで直接接続に切り替えることができます

#### ローカルSupabaseの設定

テストを実行するには、ローカルのPostgreSQLインスタンスが必要です：

```bash
# Docker経由でPostgreSQLを起動
docker run --name postgres-test -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=postgres -p 54322:5432 -d postgres:14

# マイグレーションを適用してスキーマを作成
cat supabase/migrations/20250406_initial_schema.sql | docker exec -i postgres-test psql -U postgres -d postgres
```

または、Supabase CLIを使用する場合：

```bash
# Supabase CLIのインストール（Homebrew経由）
brew install supabase/tap/supabase

# ローカルSupabaseの起動
supabase init --force
supabase start

# これにより、PostgreSQLがlocalhost:54322で利用可能になります
# ユーザー名: postgres
# パスワード: postgres（または環境変数SUPABASE_DB_PASSWORDで指定）
```

テスト実行時は、ローカルPostgreSQLが起動していることを確認してください。また、マイグレーションファイルを適用してスキーマが作成されていることを確認してください。

### コード品質

- ⚠️ **リンター警告**: 未使用のインポートや不適切なブール比較に注意
- ✅ **解決策**: `is_active == True`のような比較を`is_active`に簡略化
- ✅ **メモリエンジンのリンター修正**: 未使用のインポートを削除し、裸のexcept文を具体的な例外タイプに修正

### テスト

- ✅ **ユニットテスト**: モックを使用してデータベース接続なしでテスト可能
- ⚠️ **統合テスト**: 実際のデータベースを使用する場合は環境変数の設定が必要
- ✅ **メモリエンジンのテスト**: リンターチェックを実行し、コードの品質を確認

### 記憶管理エンジンの実装詳細

#### 階層的記憶構造

記憶は以下の階層で管理されます：

1. **daily_raw**: 生の会話データから変換された日々の記憶
2. **daily_summary**: daily_rawから生成された日単位の要約
3. **level_10**: 約10日分の記憶をまとめた要約（10倍スケール第1階層）
4. **level_100**: 約100日分の記憶をまとめた要約（10倍スケール第2階層）
5. **level_1000**: 約1000日分の記憶をまとめた要約（10倍スケール第3階層）
6. **level_archive**: 1000日を超える長期的な統合記憶（最高レベルの抽象化）

#### 睡眠時記憶処理

キャラクターの記憶整理プロセスは、夜間の睡眠セッション中に実行されます：

1. キャラクターが「睡眠状態」になると、`SleepProcessor`クラスの`start_sleep_session`メソッドが呼び出されます
2. 現在の日に対応する`daily_raw`記憶から`daily_summary`が生成されます
3. 日数に応じて、より高次の階層的記憶（level_10、level_100など）が必要に応じて生成されます
4. 記憶処理が完了すると、キャラクターの睡眠状態が解除されます

#### 設定の柔軟性

- プロンプトは`app/core/prompts/memory_prompts.py`で外部定義されており、簡単に編集可能
- LLMモデルは各クラスのコンストラクタでデフォルト値として設定され、インスタンス化時に変更可能
- 記憶タイプと階層構造は`app/core/constants/memory_types.py`で定義され、システム全体で一貫して使用
