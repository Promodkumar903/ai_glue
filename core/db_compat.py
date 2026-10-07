"""
Database compatibility layer.
Mimics sqlite3 interface but uses PostgreSQL (Supabase) under the hood.
"""
import os
import re
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv('DATABASE_URL', '')


def connect(db_path=''):
    """Return a connection that mimics sqlite3.connect()."""
    if not DATABASE_URL:
        # Fallback to SQLite for local development
        import sqlite3 as _sqlite
        return _sqlite.connect('ai_glue.db')
    return _CompatConnection(DATABASE_URL)


class _CompatConnection:
    def __init__(self, url):
        self._conn = psycopg2.connect(url)
        self._conn.autocommit = False

    def cursor(self):
        return _CompatCursor(self._conn.cursor())

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()


class _CompatCursor:
    def __init__(self, cur):
        self._cur = cur
        self.rowcount = 0
        self.lastrowid = None

    def execute(self, query, params=None):
        query = self._convert_sql(query)

        # Handle PRAGMA table_info specially
        if query.strip().upper().startswith('PRAGMA TABLE_INFO'):
            table_name = query.split('(')[1].split(')')[0].strip().strip("'").strip('"')
            query = (
                "SELECT ordinal_position AS cid, column_name AS name, "
                "data_type AS type, 0 AS notnull, NULL AS dflt_value, 0 AS pk "
                "FROM information_schema.columns WHERE table_name = %s "
                "ORDER BY ordinal_position"
            )
            self._cur.execute(query, (table_name,))
            self.rowcount = self._cur.rowcount
            return

        if params is not None:
            self._cur.execute(query, params)
        else:
            self._cur.execute(query)
        self.rowcount = self._cur.rowcount

    def executemany(self, query, params_list):
        query = self._convert_sql(query)
        self._cur.executemany(query, params_list)
        self.rowcount = self._cur.rowcount

    def fetchone(self):
        return self._cur.fetchone()

    def fetchall(self):
        return self._cur.fetchall()

    def close(self):
        self._cur.close()

    def _convert_sql(self, query):
        # 1. ? -> %s placeholder
        query = query.replace('?', '%s')

        # 2. INSERT OR IGNORE -> INSERT ... ON CONFLICT DO NOTHING
        upper = query.upper().strip()
        if upper.startswith('INSERT OR IGNORE'):
            query = 'INSERT' + query[len('INSERT OR IGNORE'):]
            query = query.rstrip().rstrip(';') + ' ON CONFLICT DO NOTHING'

        # 3. INSERT OR REPLACE -> not supported; use UPSERT logic
        # (skip - not used in our code)

        # 4. AUTOINCREMENT -> remove (Postgres handles via SERIAL/IDENTITY)
        query = query.replace('AUTOINCREMENT', '')

        # 5. INTEGER PRIMARY KEY -> SERIAL PRIMARY KEY (only if standalone)
        # (skip - our tables use TEXT PRIMARY KEY)

        # 6. GROUP_CONCAT(x) -> STRING_AGG(x, ',')
        if 'GROUP_CONCAT' in query.upper():
            query = re.sub(
                r"GROUP_CONCAT\s*\(\s*([^,)]+)\s*\)",
                r"STRING_AGG(\1, ',')",
                query,
                flags=re.IGNORECASE
            )

        return query