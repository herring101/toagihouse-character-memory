import os
import re
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_DB_PASSWORD = os.environ.get("SUPABASE_DB_PASSWORD")

DATABASE_URL = os.environ.get("DATABASE_URL")

print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"DATABASE_URL: {DATABASE_URL}")

if not DATABASE_URL and SUPABASE_URL and SUPABASE_DB_PASSWORD:
    host_match = re.search(r'https://([^.]+)\.supabase\.co', SUPABASE_URL)
    if host_match:
        host_id = host_match.group(1)
        DATABASE_URL = f"postgresql://postgres:{SUPABASE_DB_PASSWORD}@db.{host_id}.supabase.co:5432/postgres"
        print(f"Supabase直接接続: db.{host_id}.supabase.co:5432")
    else:
        DATABASE_URL = f"postgresql://postgres:{SUPABASE_DB_PASSWORD}@localhost:54322/postgres"
        print("ローカル接続: localhost:54322")
elif not DATABASE_URL:
    DATABASE_URL = f"postgresql://postgres:{SUPABASE_DB_PASSWORD}@localhost:54322/postgres"
    print("ローカル接続: localhost:54322")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
