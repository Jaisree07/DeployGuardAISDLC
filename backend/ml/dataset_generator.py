import random
import pandas as pd
from pathlib import Path


class DatasetGenerator:

    OUTPUT_FILE = "datasets/ml_ready_dataset.csv"

    @staticmethod
    def generate(records=500):

        data = []

        environments = ["DEV", "QA", "UAT", "PROD"]

        for _ in range(records):

            environment = random.choice(environments)

            cpu = random.randint(5, 100)
            memory = random.randint(10, 100)
            latency = random.randint(50, 1000)
            build_duration = random.randint(10, 300)
            deployment_duration = random.randint(5, 120)
            error_count = random.randint(0, 6)

            deployment_success = 1

            if (
                cpu > 85
                or memory > 85
                or latency > 700
                or error_count > 2
            ):
                deployment_success = 0

            row = {

                "environment_encoded":
                    {
                        "DEV": 0,
                        "QA": 1,
                        "UAT": 2,
                        "PROD": 3
                    }[environment],

                "cpu_usage": cpu,
                "memory_usage": memory,
                "latency": latency,
                "build_duration": build_duration,
                "deployment_duration": deployment_duration,
                "error_count": error_count,

                "high_cpu": int(cpu > 80),
                "high_memory": int(memory > 80),
                "high_latency": int(latency > 500),
                "deployment_failed": int(error_count > 0),

                "deployment_success": deployment_success
            }

            data.append(row)

        df = pd.DataFrame(data)

        Path("datasets").mkdir(exist_ok=True)

        df.to_csv(
            DatasetGenerator.OUTPUT_FILE,
            index=False
        )

        print(df.head())

        print("\nDataset Shape:", df.shape)

        print("\nClass Distribution:")

        print(df["deployment_success"].value_counts())


if __name__ == "__main__":
    DatasetGenerator.generate()