"""
PostgreSQL Smoke Test
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
load_dotenv()

def test_postgres():
    db_url = os.getenv("DATABASE_URL")
    if not db_url or "postgresql" not in db_url:
        print("❌ DATABASE_URL is not PostgreSQL")
        return False

    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ PostgreSQL connection successful:", result.fetchone())
        return True
    except Exception as e:
        print("❌ PostgreSQL Connection Failed:", e)
        return False

if __name__ == "__main__":
    test_postgres()