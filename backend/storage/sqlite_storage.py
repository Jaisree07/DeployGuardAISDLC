import sqlite3
from pathlib import Path

DB_PATH = Path("deployguard.db")


class SQLiteStorage:

    @staticmethod
    def initialize():

        print(f"[SQLite] Initializing database at: {DB_PATH.resolve()}")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS deployment_signals (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                deployment_name TEXT,

                environment TEXT,

                status TEXT,

                source TEXT,

                timestamp TEXT,

                sync_status TEXT,

                health_status TEXT,

                revision TEXT,

                namespace TEXT,

                cluster TEXT

            )
            """
        )

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

            # Safe handling for signals that do not contain ArgoCD information
            argocd = signal.get("argocd", {})

            cursor.execute(
                """
                INSERT INTO deployment_signals
                (
                    deployment_name,
                    environment,
                    status,
                    source,
                    timestamp,

                    sync_status,
                    health_status,
                    revision,
                    namespace,
                    cluster
                )

                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    signal.get("deployment_name"),
                    signal.get("environment"),
                    signal.get("status"),
                    signal.get("source"),
                    signal.get("timestamp"),

                    argocd.get("sync_status"),
                    argocd.get("health_status"),
                    argocd.get("revision"),
                    argocd.get("namespace"),
                    argocd.get("cluster"),
                )
            )

            conn.commit()

            print("Rows inserted :", cursor.rowcount)
            print("Last Row ID   :", cursor.lastrowid)

            cursor.execute(
                "SELECT COUNT(*) FROM deployment_signals"
            )

            total = cursor.fetchone()[0]

            print("Total rows :", total)

            cursor.execute(
                "SELECT * FROM deployment_signals ORDER BY id DESC LIMIT 1"
            )

            latest = cursor.fetchone()

            print("\nLatest Record")
            print(latest)

            conn.close()

            print("\nSQLite connection closed.")
            print("========== SQLITE DEBUG END ==========\n")

        except Exception as e:

            print("\n========== SQLITE ERROR ==========")
            print(type(e).__name__)
            print(str(e))
            print("==================================\n")