import sqlite3
import pandas as pd


class FeatureEngineering:

    DATABASE = "deployguard.db"

    @staticmethod
    def load_signals():

        conn = sqlite3.connect(FeatureEngineering.DATABASE)

        query = """
        SELECT
            d.id,
            d.deployment_name,
            d.environment,
            d.status,
            t.cpu_usage,
            t.memory_usage,
            t.latency,
            t.build_duration,
            t.deployment_duration,
            t.error_count
        FROM deployments d
        INNER JOIN telemetry t
            ON d.id = t.deployment_id
        """

        df = pd.read_sql_query(query, conn)

        conn.close()

        return df

    @staticmethod
    def generate_features():

        df = FeatureEngineering.load_signals()

        if df.empty:
            return df

        # Target column
        df["deployment_success"] = (
            df["status"] == "Running"
        ).astype(int)

        # Environment Encoding
        environment_map = {
            "DEV": 0,
            "QA": 1,
            "UAT": 2,
            "PROD": 3
        }

        df["environment_encoded"] = (
            df["environment"]
            .map(environment_map)
            .fillna(0)
            .astype(int)
        )

        # Engineered Features
        df["high_cpu"] = (
            df["cpu_usage"] > 80
        ).astype(int)

        df["high_memory"] = (
            df["memory_usage"] > 80
        ).astype(int)

        df["high_latency"] = (
            df["latency"] > 500
        ).astype(int)

        df["deployment_failed"] = (
            df["error_count"] > 0
        ).astype(int)

        return df

    @staticmethod
    def export_dataset():

        df = FeatureEngineering.generate_features()

        if not df.empty:
            df.to_csv(
                "datasets/ml_ready_dataset.csv",
                index=False
            )

        return df

    @staticmethod
    def get_statistics():

        df = FeatureEngineering.generate_features()

        if df.empty:
            return {
                "message": "No data available."
            }

        return {
            "total_records": len(df),
            "successful_deployments": int(df["deployment_success"].sum()),
            "failed_deployments": int(df["deployment_failed"].sum()),
            "success_rate": round(
                (df["deployment_success"].mean() * 100), 2
            ),
            "average_cpu": round(df["cpu_usage"].mean(), 2),
            "average_memory": round(df["memory_usage"].mean(), 2),
            "average_latency": round(df["latency"].mean(), 2),
            "average_build_duration": round(df["build_duration"].mean(), 2),
            "average_deployment_duration": round(
                df["deployment_duration"].mean(), 2
            )
        }


if __name__ == "__main__":

    dataset = FeatureEngineering.export_dataset()

    print(dataset.head())

    print("\nDataset Statistics\n")

    print(FeatureEngineering.get_statistics())