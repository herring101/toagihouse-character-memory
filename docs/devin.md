# ToagiHouse Character Memory System - Supabase接続設定ガイド

## 概要

このドキュメントはToagiHouse Character Memory Systemプロジェクトにおける、Supabase接続設定の実装手順と注意点をまとめたものです。

## 必要な環境変数

以下の環境変数を`.env.local`ファイルに設定します：

```
# 既存の環境変数
OPENAI_API_KEY="your-openai-api-key"
GEMINI_API_KEY="your-gemini-api-key"
ANTHROPIC_API_KEY="your-anthropic-api-key"

# Supabase接続用環境変数
SUPABASE_URL="https://your-project-id.supabase.co"
SUPABASE_ANON_KEY="your-supabase-anon-key"
SUPABASE_DB_PASSWORD="your-database-password"
DATABASE_URL="postgresql://postgres:your-password@localhost:54322/postgres"
```

注意：
- `SUPABASE_URL`と`SUPABASE_ANON_KEY`はSupabaseダッシュボードの「Settings > API」から取得できます
- ローカル開発時は`DATABASE_URL`は`postgresql://postgres:${SUPABASE_DB_PASSWORD}@localhost:54322/postgres`のような形式になります

## フロントエンド(Next.js)の設定

### 1. Supabaseクライアントのインストール

```bash
cd ~/repos/toagihouse-character-memory/chat-app
npm install @supabase/supabase-js
```

### 2. Supabaseクライアントの設定

`chat-app/src/lib/supabase.ts`ファイルを作成し、以下のコードを追加します：

```typescript
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('Supabase URL or Anon Key is missing');
}

const supabase = createClient(supabaseUrl, supabaseAnonKey);

export default supabase;
```

## バックエンド(FastAPI)の設定

### 1. 必要なパッケージのインストール

```bash
cd ~/repos/toagihouse-character-memory/backend
source venv/bin/activate
pip install psycopg2-binary sqlalchemy supabase
```

### 2. データベース接続の設定

`backend/database.py`ファイルを作成し、以下のコードを追加します：

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
    raise Exception("DATABASE_URL environment variable is not set")

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

## 開発時の注意点

1. **ローカル開発とSupabase CLI**:
   - Supabase CLIを使用すると、ローカル開発環境でSupabaseを実行できます
   - `supabase/config.toml`ファイルにはポート設定があり、ローカルではデータベースは54322ポートで実行されます

2. **セキュリティに関する注意**:
   - 実際の開発では`.env.local`ファイルをGitにコミットしないよう注意してください
   - Row Level Security (RLS)ポリシーが適切に設定されていることを確認してください

3. **未実装の部分**:
   - フロントエンドとバックエンドからのSupabase接続は未実装です
   - データアクセス関数(CRUD操作)の実装が必要です

4. **開発中に気づいた点**:
   - 現在のプロジェクトでは、Supabaseクライアントが未導入です
   - `.env.local`ファイルにはSUPABASE_DB_PASSWORDは設定されていますが、SUPABASE_URLやSUPABASE_ANON_KEYが設定されていません
   - バックエンドの`requirements.txt`にはデータベース接続用のパッケージが含まれていないため、追加が必要です

5. **次回の開発に向けて**:
   - タスク1.2「データアクセス関数の実装」では、このドキュメントを参考にSupabase接続を実装してから、CRUD操作を実装することをお勧めします
   - 実装前に、Supabaseプロジェクトの設定（URL、APIキー）を確認してください
   - ローカル開発環境でSupabaseを実行する場合は、Supabase CLIのインストールと設定が必要です
