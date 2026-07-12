from fastapi import APIRouter
import sqlite3

router = APIRouter(
    prefix="/signals",
    tags=["Signals"]
)


@router.get("/")
def get_signals():

    conn = sqlite3.connect("deployguard.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM deployment_signals
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]