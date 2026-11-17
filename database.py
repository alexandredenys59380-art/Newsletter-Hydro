import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("data/edf_hydro_watch.db")

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    with connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT,
                source TEXT,
                published TEXT,
                summary TEXT,
                category TEXT,
                collected_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

def save_article(article):
    with connect() as con:
        cur = con.execute("""
            INSERT OR IGNORE INTO articles(url, title, source, published, summary, category)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            article["url"], article["title"], article["source"],
            article["published"], article["summary"], article["category"]
        ))
        return cur.rowcount == 1

def get_articles():
    with connect() as con:
        return pd.read_sql_query(
            "SELECT * FROM articles ORDER BY published DESC, id DESC", con
        )
