import sqlite3
from pathlib import Path

DB_PATH = Path("deployguard.db")


class SQLiteStorage:

    @staticmethod
    def initialize():
        print(f"[SQLite] Initializing database at: {DB_PATH.resolve()}")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS deployment_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deployment_name TEXT,
            environment TEXT,
            status TEXT,
            source TEXT,
            timestamp TEXT
        )
        """)

        conn.commit()
        conn.close()

        print("[SQLite] deployment_signals table is ready.")

    @staticmethod
    def save(signal):

        print("\n========== SQLITE DEBUG ==========")
        print("Database:", DB_PATH.resolve())
        print("Signal received:", signal)

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO deployment_signals
                (
                    deployment_name,
                    environment,
                    status,
                    source,
                    timestamp
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    signal["deployment_name"],
                    signal["environment"],
                    signal["status"],
                    signal["source"],
                    signal["timestamp"]
                )
            )

            conn.commit()

            print("Rows inserted:", cursor.rowcount)
            print("Last Row ID:", cursor.lastrowid)

            cursor.execute("SELECT COUNT(*) FROM deployment_signals")
            total = cursor.fetchone()[0]

            print("Total rows in deployment_signals:", total)

            conn.close()

            print("SQLite connection closed.")
            print("========== SQLITE DEBUG END ==========\n")

        except Exception as e:
            print("SQLite Error:", e)