import os
import re
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_DB_PASSWORD = os.environ.get("SUPABASE_DB_PASSWORD")

print(f"SUPABASE_URL: {SUPABASE_URL}")

if SUPABASE_DB_PASSWORD:
    if SUPABASE_URL:
        host_match = re.search(r'https://([^.]+)\.supabase\.co', SUPABASE_URL)
        if host_match:
            host_id = host_match.group(1)
            DATABASE_URL = f"postgresql://postgres:{SUPABASE_DB_PASSWORD}@localhost:54322/postgres"
            print("ローカル接続を使用: localhost:54322")
            # DATABASE_URL = f"postgresql://postgres:{SUPABASE_DB_PASSWORD}@db.{host_id}.supabase.co:5432/postgres"
            # print(f"Supabase直接接続を使用: db.{host_id}.supabase.co:5432")
        else:
            DATABASE_URL = f"postgresql://postgres:{SUPABASE_DB_PASSWORD}@localhost:54322/postgres"
            print("ローカル接続を使用: localhost:54322")
    else:
        DATABASE_URL = f"postgresql://postgres:{SUPABASE_DB_PASSWORD}@localhost:54322/postgres"
        print("ローカル接続を使用: localhost:54322")
else:
    print("警告: SUPABASE_DB_PASSWORDが設定されていません。")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
