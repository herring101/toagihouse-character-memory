# ToagiHouse Character Memory System

## 概要

ToagiHouse Character Memory System は、キャラクターの記憶を管理するためのデータベースシステムです。キャラクターごとに異なるタイプの記憶（日常的な記憶から長期的な記憶まで）を保存・管理することができます。

## 機能

- キャラクター情報の管理
- 様々なタイプの記憶（daily, deca, centi, kilo, mega, tera）の保存
- 日数範囲に基づいた記憶の管理
- セッション管理による同時接続の制限

## データベース構造

### characters テーブル

キャラクター情報を管理するテーブル

- `id`: UUID (PK)
- `user_id`: UUID
- `name`: TEXT
- `config`: JSONB（将来的な拡張用）
- `created_at`: TIMESTAMPTZ

### memories テーブル

キャラクターの記憶を管理するテーブル

- `id`: UUID (PK)
- `user_id`: UUID
- `character_id`: UUID (FK → characters.id)
- `memory_type`: TEXT（例："daily", "deca", "centi", "kilo", "mega", "tera"）
- `start_day`: INTEGER
- `end_day`: INTEGER
- `content`: TEXT
- `created_at`: TIMESTAMPTZ

### sessions テーブル

ユーザーセッションを管理するテーブル

- `id`: UUID (PK)
- `user_id`: UUID
- `character_id`: UUID (FK → characters.id)
- `device_id`: TEXT
- `is_active`: BOOLEAN
- `started_at`: TIMESTAMPTZ
- `last_updated_at`: TIMESTAMPTZ

## セットアップ

### 前提条件

- Supabase CLI
- Node.js

### インストール

1. リポジトリをクローン

   ```bash
   git clone https://github.com/herring101/toagihouse-character-memory.git
   cd toagihouse-character-memory
   ```

2. Supabase プロジェクトとリンク

   ```bash
   supabase init
   supabase link --project-ref your-project-ref
   ```

3. データベースマイグレーションを適用
   ```bash
   supabase db push
   ```

## 使用方法

Supabase SDK を使用して、データベースに接続し、キャラクターや記憶を管理できます。詳細な API ドキュメントは今後追加予定です。

## セキュリティ

- すべてのテーブルに Row Level Security (RLS)が適用されています
- ユーザーは自分のデータのみにアクセスできます

## ライセンス

MIT
