# ToagiHouse Character Memory System プロジェクト構造概要

## セットアップと実行方法

### 前提条件
- Node.js 18以上
- Python 3.8以上
- npm または yarn

### 初期セットアップ

```bash
# 初期セットアップスクリプトを実行
./setup.sh
```

このスクリプトは以下の処理を自動的に行います：
- `.env.local` ファイルのテンプレートを作成（初回のみ）
- フロントエンド依存関係のインストール（npm install）
- バックエンド用の仮想環境作成とパッケージインストール

`.env.local` ファイルに少なくとも一つのLLM APIキーを設定してください：
- `OPENAI_API_KEY`
- `GEMINI_API_KEY` / `GOOGLE_API_KEY`
- `ANTHROPIC_API_KEY`

### アプリケーションの起動

```bash
# フロントエンドとバックエンドを同時に起動
./start-app.sh
```

- フロントエンド: http://localhost:3000
- バックエンド: http://localhost:8000

## 現在のプロジェクト構成

### 全体構造

- プロジェクトルート：基本設定ファイル（package.json, README.md, .gitignore）
- `supabase/`：Supabase 関連設定とマイグレーションファイル
- `chat-app/`：Next.js ベースのフロントエンドアプリケーション
- `chat-app/backend/`：FastAPI + LiteLLM ベースのバックエンド

### フロントエンド (Next.js)

- Next.js 15.2.4、React 19、TypeScript 使用
- Tailwind CSS と shadcn/UI コンポーネントライブラリでスタイリング
- チャットインターフェース実装済み
- 複数の AI モデル（Gemini、OpenAI、Anthropic）切り替え機能

### バックエンド (FastAPI + LiteLLM)

- FastAPI フレームワークで REST API 構築
- LiteLLM で複数の AI プロバイダー（Google、OpenAI、Anthropic）と統合
- ストリーミング/非ストリーミングモードサポート
- モデル一覧取得とチャット機能のエンドポイント提供

### データベース設計 (Supabase/PostgreSQL)

初期スキーマでは以下のテーブルが定義済み：

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
   - `memory_type`: TEXT ('daily', 'deca', 'centi', 'kilo', 'mega', 'tera'等)
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

適切なインデックスと Row Level Security（RLS）ポリシーも設定済み。

## 実装予定の機能構造

### 「記憶機能」の階層設計

階層的な記憶構造を実装予定：

- **daily_raw**：日々の生の会話・作業記録
- **daily_summary**：1日の記憶をまとめたもの
- **level_10**：約10日分の記憶をまとめたもの（10倍スケールの第1階層）
- **level_100**：約100日分の記憶をまとめたもの（10倍スケールの第2階層）
- **level_1000**：約1000日（約3年）分の記憶をまとめたもの（10倍スケールの第3階層）
- **level_archive**：1000日を超える長期的な統合記憶

### 「セッション」機能

セッション開始時に以下の記憶をシステムプロンプトに含める：

- その日の会話・作業記録
- 直前 10 個の各階層記憶（思い出メモ、x10、x100、x1000 など）

データベースと連携し、キャラクターの記憶を階層的に保存・取得する機能が必要になります。既存のチャットインターフェースと記憶システムを統合するための開発が次のステップになります。
