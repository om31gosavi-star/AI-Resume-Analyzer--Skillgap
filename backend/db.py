"""Database helpers for SkillGap (SQLite)."""
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "..", "database")
DB_PATH = os.environ.get("SKILLGAP_DB", os.path.join(DB_DIR, "skillgap.db"))


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(force=False):
    """Create tables and load seed data (only if the database is new)."""
    exists = os.path.exists(DB_PATH)
    if exists and not force:
        return
    if exists and force:
        os.remove(DB_PATH)
    conn = get_conn()
    for name in ("schema.sql", "seed.sql"):
        with open(os.path.join(DB_DIR, name), encoding="utf-8") as f:
            conn.executescript(f.read())
    conn.commit()
    conn.close()
