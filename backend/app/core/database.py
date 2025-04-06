import os
import re

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 環境変数から接続情報を取得
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_DB_PASSWORD = os.environ.get("SUPABASE_DB_PASSWORD", "")

# データベース接続URLの構築
if SUPABASE_DB_PASSWORD:
    if SUPABASE_URL:
        host_match = re.search(r"https://([^.]+)\.supabase\.co", SUPABASE_URL)
        if host_match:
            host_id = host_match.group(1)
            # ローカル開発環境ではlocalhost:54322に接続
            DATABASE_URL = (
                f"postgresql://postgres:{SUPABASE_DB_PASSWORD}@localhost:54322/postgres"
            )
            print("ローカル開発環境のSupabaseに接続: localhost:54322")
        else:
            # ホスト名が取得できない場合もローカル接続を使用
            DATABASE_URL = (
                f"postgresql://postgres:{SUPABASE_DB_PASSWORD}@localhost:54322/postgres"
            )
            print("ローカル開発環境のSupabaseに接続: localhost:54322")
    else:
        # SUPABASE_URLが設定されていない場合もローカル接続
        DATABASE_URL = (
            f"postgresql://postgres:{SUPABASE_DB_PASSWORD}@localhost:54322/postgres"
        )
        print("ローカル開発環境のSupabaseに接続: localhost:54322")
else:
    # テスト用にSQLiteを使用
    DATABASE_URL = "sqlite:///:memory:"
    print("SQLiteのインメモリデータベースを使用します（テスト用）")

# SQLAlchemyエンジンとセッションの作成
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    データベースセッションの依存性注入用関数

    FastAPIのDependencyとして使用される
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
