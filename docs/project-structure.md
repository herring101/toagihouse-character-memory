# ToagiHouse Character Memory System プロジェクト構造

## 1. プロジェクト概要

ToagiHouse Character Memory Systemは、AI キャラクターに階層的な記憶機能を提供するプラットフォームです。ユーザーが AI キャラクターと継続的な会話を行い、キャラクターがさまざまなレベルの詳細と時間枠で過去のやり取りを記憶できるようにします。このシステムは、生の会話から長期的な抽象的な要約まで、記憶を整理する洗練された階層的記憶構造を実装することで、自然かつコンテキストを意識した会話を可能にします。

## 2. 全体構造

プロジェクトは以下の主要コンポーネントで構成されています：

### プロジェクトディレクトリ構造

```
toagihouse-character-memory/
├── supabase/             # Supabase関連設定とマイグレーションファイル
├── chat-app/             # Next.jsベースのフロントエンドアプリケーション
│   └── backend/          # FastAPI + LiteLLMベースのバックエンド
├── docs/                 # プロジェクトドキュメント
├── setup.sh              # 初期セットアップスクリプト
├── start-app.sh          # アプリケーション起動スクリプト
└── README.md             # プロジェクト概要
```

### コアシステムとサービス

1. **フロントエンド (Next.js アプリケーション)**
   - `chat-app/src` ディレクトリに配置
   - ユーザーインタラクション用のチャットインターフェースを提供
   - 複数のAIモデル（Gemini、OpenAI、Anthropic）をサポート
   - ストリーミングおよび非ストリーミングレスポンスを実装

2. **バックエンド (FastAPI)**
   - `chat-app/backend` ディレクトリに配置
   - チャットとメモリ操作のAPIリクエストを処理
   - LiteLLM経由でAIプロバイダーと統合
   - メモリ管理エンジンを管理

3. **データベース (Supabase/PostgreSQL)**
   - `supabase` ディレクトリに配置
   - キャラクター情報、メモリデータ、セッションデータを保存
   - スキーマは`supabase/migrations`ディレクトリに定義
   - データ保護のためのRow Level Securityを実装

4. **メモリ管理エンジン**
   - メモリの保存、取得、要約のためのコアシステム
   - 階層的メモリ構造を実装
   - 生の会話を構造化メモリに変換
   - セッションコンテキストに関連するメモリを選択

## 3. バックエンド構造

バックエンドはFastAPIを使用して構築され、以下のような構造になっています：

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

### 主な機能

- **FastAPIフレームワーク**: RESTful APIの構築に使用
- **LiteLLM統合**: 複数のAIプロバイダー（Google、OpenAI、Anthropic）との連携
- **ストリーミング/非ストリーミング**: 両方のモードをサポート
- **モジュール化**: 明確に分離された責任を持つコンポーネント
- **SQLAlchemy ORM**: データベースとのやり取りに使用
- **テスト**: 単体テストとモックを実装

## 4. フロントエンド構造

フロントエンドはNext.jsを使用して構築され、以下のような構造になっています：

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

### 主な機能

- **Next.js 15.2.4**: Reactフレームワークとして使用
- **React 19**: UIコンポーネントライブラリ
- **TypeScript**: 型安全性の確保
- **Tailwind CSS**: スタイリングに使用
- **shadcn/UI**: UIコンポーネントライブラリ
- **チャットインターフェース**: 対話型UIの実装
- **複数モデルサポート**: 異なるAIモデル間の切り替え機能

## 5. データベース設計

Supabase/PostgreSQLを使用したデータベース設計は以下のとおりです：

### テーブル構造

1. **characters**：キャラクター基本情報
   - `id`: UUID (PK)
   - `user_id`: UUID
   - `name`: TEXT
   - `config`: JSONB (将来拡張用)
   - `created_at`: TIMESTAMPTZ

2. **memories**：キャラクターの記憶データ
   - `id`: UUID (PK)
   - `user_id`: UUID
   - `character_id`: UUID (FK)
   - `memory_type`: TEXT ('daily_raw', 'daily_summary', 'level_10', 'level_100', 'level_1000', 'level_archive'等)
   - `start_day`: INTEGER
   - `end_day`: INTEGER
   - `content`: TEXT
   - `created_at`: TIMESTAMPTZ

3. **sessions**：ユーザーセッション管理
   - `id`: UUID (PK)
   - `user_id`: UUID
   - `character_id`: UUID (FK)
   - `device_id`: TEXT
   - `is_active`: BOOLEAN
   - `started_at`/`last_updated_at`: TIMESTAMPTZ

### セキュリティ

- Row Level Security (RLS)ポリシーによるデータ保護
- 適切なインデックスによるパフォーマンス最適化

## 6. 記憶階層構造

本システムは以下の階層的記憶構造を実装しています：

1. **daily_raw**: 生の会話データから変換された日々の記憶。記憶テーブルにmemory_type='daily_raw'として保存。未処理の対話を含む。

2. **daily_summary**: daily_rawから生成された日単位の要約。記憶テーブルにmemory_type='daily_summary'として保存。生データよりも簡潔。

3. **level_10**: 約10日分の記憶をまとめた要約。記憶テーブルにmemory_type='level_10'として保存。階層的記憶の第1レベル。

4. **level_100**: 約100日分の記憶をまとめた要約。記憶テーブルにmemory_type='level_100'として保存。階層的記憶の第2レベル。

5. **level_1000**: 約1000日（約3年）分の記憶をまとめた要約。記憶テーブルにmemory_type='level_1000'として保存。階層的記憶の第3レベル。

6. **level_archive**: 1000日を超える長期的な統合記憶。記憶テーブルにmemory_type='level_archive'として保存。最高レベルの抽象化。

この階層構造は記憶の時間スケールと抽象化レベルによって整理され、daily_raw → daily_summary → level_10 → level_100 → level_1000 → level_archiveの順に進行します。

## 7. 睡眠処理メカニズム

キャラクターの記憶整理プロセスは、睡眠セッション中に実行されます：

1. `SleepProcessor.start_sleep_session(current_day)`メソッドで睡眠セッションを開始
2. 現在の日に対応する`daily_raw`記憶から`daily_summary`を生成
3. 日数に応じて、階層的記憶（level_10、level_100など）を生成
4. セッションステータスを「完了」に更新し、処理結果を返す

このプロセスはLLMを使用して実行され、プロンプトとモデルは外部ファイルで設定可能です。

## 8. 現在の実装状況

### 完了済みコンポーネント

- ✅ **データベース接続**: Supabaseとの連携設定
- ✅ **データモデル**: 基本的なSQLAlchemyモデル（Character, Memory, Session）
- ✅ **CRUD操作**: SQLAlchemy ORM経由でのデータアクセス関数
- ✅ **記憶管理エンジン**: 階層的記憶の生成・取得・処理ロジック
- ✅ **基本チャットAPI**: テキスト生成APIエンドポイント
- ✅ **単体テスト**: CRUD操作と記憶エンジンの単体テスト（モック対応済み）

### 現在実装中

- 🔄 **APIレイヤーの拡張**: キャラクター管理、記憶管理のAPIエンドポイント
- 🔄 **セッション管理API**: 会話・睡眠セッションのエンドポイント

### 次に実装予定

- 📅 **キャラクターUI**: キャラクター管理画面とチャットインターフェース統合
- 📅 **記憶閲覧UI**: 階層的記憶の視覚化
- 📅 **セッション管理UI**: 会話・睡眠状態の制御インターフェース

## 9. セットアップと実行方法

### 前提条件
- Node.js 18以上
- Python 3.8以上
- npm または yarn

### 環境変数
以下の環境変数の設定が必要です：
- LLM APIキー（少なくとも一つ）: `OPENAI_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`
- Supabase接続情報: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_DB_PASSWORD`

### 初期セットアップ
```bash
# 初期セットアップスクリプトを実行
./setup.sh
```

### アプリケーションの起動
```bash
# フロントエンドとバックエンドを同時に起動
./start-app.sh
```

- フロントエンド: http://localhost:3000
- バックエンド: http://localhost:8000
