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

- **Phase 1.3**: 追加マイグレーションとRLS設定
- **Phase 2**: 記憶管理エンジンの実装

## 注意点と解決済みの問題

### 環境変数

- ✅ **dotenv依存関係の削除**: 環境変数は`os.environ.get()`で直接取得するように変更
- ⚠️ **必要な環境変数**:
  - LLM API: `OPENAI_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`（少なくとも1つ）
  - Supabase: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_DB_PASSWORD`

### データベース接続

- ⚠️ **Supabaseへの直接接続制限**: Supabaseデータベースへの直接PostgreSQL接続（ポート5432）は失敗する可能性があります
- ✅ **解決策**: Supabase REST APIを使用するか、ローカル開発環境でSupabase CLIを使用

### コード品質

- ⚠️ **リンター警告**: 未使用のインポートや不適切なブール比較に注意
- ✅ **解決策**: `is_active == True`のような比較を`is_active`に簡略化

### テスト

- ✅ **ユニットテスト**: モックを使用してデータベース接続なしでテスト可能
- ⚠️ **統合テスト**: 実際のデータベースを使用する場合は環境変数の設定が必要
