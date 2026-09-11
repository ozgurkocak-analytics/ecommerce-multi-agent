import sqlite3
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agents.schemas import SentimentAnalysisResult

DB_PATH = ROOT_DIR / "data" / "sales.db"

def apply_sentiment_updates(updates: list[SentimentAnalysisResult]) -> int:
    """İnsan onayından geçen analiz sonuçlarını SQLite reviews tablosuna yazar."""
    if not updates:
        return 0

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updated_count = 0
    for item in updates:
        cursor.execute(
            """
            UPDATE reviews
            SET sentiment = ?,
                issue_type = ?,
                flagged_for_ops = ?
            WHERE review_id = ?;
            """,
            (item.sentiment, item.issue_type, int(item.flagged_for_ops), item.review_id)
        )
        updated_count += cursor.rowcount

    conn.commit()
    conn.close()
    return updated_count