"""
Migrate SQLite to PostgreSQL (or just create tables in PostgreSQL)
"""
import os
from sqlalchemy import create_engine
from core.database import Base
from dotenv import load_dotenv

load_dotenv()

def migrate():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not set in .env")
        return
    
    print(f"📦 Connecting to: {db_url}")
    engine = create_engine(db_url, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    print("✅ All tables created successfully!")

if __name__ == "__main__":
    migrate()