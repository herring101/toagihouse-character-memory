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
pytest

# 特定のテストのみ実行
pytest app/tests/test_crud.py -v
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
│   │   ├── constants.py    # 定数定義（記憶タイプなど）
│   │   ├── database.py     # データベース接続設定
│   │   └── prompts.py      # LLMプロンプトテンプレート
│   ├── crud/               # データアクセス関数
│   │   ├── character.py    # キャラクター管理関数
│   │   ├── memory.py       # 記憶管理関数
│   │   └── session.py      # セッション管理関数
│   ├── memory/             # 記憶管理エンジン
│   │   ├── generator.py    # 記憶生成エンジン
│   │   ├── processor.py    # 睡眠処理エンジン
│   │   └── retriever.py    # 記憶取得エンジン
│   ├── models.py           # SQLAlchemyモデル定義
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
│   │   ├── api/            # APIクライアント
│   │   └── page.tsx        # メインページ
│   ├── components/         # Reactコンポーネント
│   │   └── chat/           # チャット関連コンポーネント
│   └── lib/                # ユーティリティ
│       └── supabase.ts     # Supabaseクライアント
└── package.json            # 依存関係定義
```

## 実装の進捗

### 完了したコンポーネント

- ✅ **データベース接続**: Supabase との連携設定
- ✅ **データモデル**: 基本的な SQLAlchemy モデル（Character, Memory, Session）
- ✅ **CRUD 操作**: SQLAlchemy ORM 経由でのデータアクセス関数
- ✅ **記憶管理エンジン**: 階層的記憶の生成・取得・処理ロジック
- ✅ **基本チャット API**: テキスト生成 API エンドポイント
- ✅ **単体テスト**: CRUD 操作と記憶エンジンの単体テスト（モック対応済み）

### 現在実装中

- 🔄 **API レイヤーの拡張**: キャラクター管理、記憶管理の API エンドポイント
- 🔄 **セッション管理 API**: 会話・睡眠セッションのエンドポイント

### 次に実装予定

- 📅 **キャラクター UI**: キャラクター管理画面とチャットインターフェース統合
- 📅 **記憶閲覧 UI**: 階層的記憶の視覚化
- 📅 **セッション管理 UI**: 会話・睡眠状態の制御インターフェース

## テスト方法

### 実際の LLM API を使用したテスト

実際の LLM API を使用したテストを行う場合は、以下の環境変数を設定してください：

```bash
# いずれかのAPIキーを設定
export OPENAI_API_KEY="your-openai-api-key"
export GEMINI_API_KEY="your-gemini-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

## 記憶階層構造

本システムは以下の階層的記憶構造を実装しています：

1. **daily_raw**: 生の会話データから変換された日々の記憶
2. **daily_summary**: daily_raw から生成された日単位の要約
3. **level_10**: 約 10 日分の記憶をまとめた要約（10 倍スケール第 1 階層）
4. **level_100**: 約 100 日分の記憶をまとめた要約（10 倍スケール第 2 階層）
5. **level_1000**: 約 1000 日分の記憶をまとめた要約（10 倍スケール第 3 階層）
6. **level_archive**: 1000 日を超える長期的な統合記憶（最高レベルの抽象化）

この階層構造は `app/core/constants.py`で定義されており、記憶管理エンジンがこれに従って記憶の生成と取得を行います。

## 睡眠処理メカニズム

キャラクターの記憶整理プロセスは、睡眠セッション中に実行されます：

1. `SleepProcessor.start_sleep_session(current_day)`メソッドで睡眠セッションを開始
2. 現在の日に対応する `daily_raw`記憶から `daily_summary`を生成
3. 日数に応じて、階層的記憶（level_10、level_100 など）を生成
4. セッションステータスを「完了」に更新し、処理結果を返す

睡眠処理テストは `test_memory.py`で実装されており、実際の LLM 呼び出しをモック化してテストします。

## 注意点と対策

### 環境変数

- ⚠️ **必要な環境変数**:
  - LLM API: `OPENAI_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`（少なくとも 1 つ）
  - Supabase: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_DB_PASSWORD`

### データベース接続

- ローカル開発環境では `localhost:54322`への PostgreSQL 接続を使用
- Supabase CLI を使用する場合はローカル DB が自動的に起動します
- テスト実行時はインメモリ SQLite を使用するため、DB 設定は不要

### テスト

- モックを使用することで、実際の LLM API に接続せずにテストを実行可能
- テスト実行前にはリンターチェックを推奨: `ruff check .`
- `pytest`コマンドで全テストを実行、`pytest -v`で詳細出力
- `pytest -k "test_name"`で特定のテストのみ実行可能

## 今後の開発計画

1. API レイヤーの拡張（キャラクター・記憶・セッション管理）
2. フロントエンド UI の実装（キャラクター管理、記憶閲覧）
3. チャットインターフェースとの統合
4. エンドツーエンドテストの実装
5. デプロイ準備

詳細な計画は `docs/plan.md`を参照してください。
