import random
import pandas as pd
from pathlib import Path


class DatasetGenerator:

    OUTPUT_FILE = "datasets/ml_ready_dataset.csv"

    @staticmethod
    def generate(records=500):

        data = []

        environments = ["DEV", "QA", "UAT", "PROD"]

        environment_encoding = {
            "DEV": 0,
            "QA": 1,
            "UAT": 2,
            "PROD": 3
        }

        for _ in range(records):

            environment = random.choice(environments)

            cpu = random.randint(5, 100)
            memory = random.randint(10, 100)
            latency = random.randint(50, 1000)
            build_duration = random.randint(10, 300)
            deployment_duration = random.randint(5, 120)
            error_count = random.randint(0, 6)

            # -----------------------------------------
            # Feature Engineering
            # -----------------------------------------

            high_cpu = int(cpu > 80)
            high_memory = int(memory > 80)
            high_latency = int(latency > 500)
            deployment_failed = int(error_count > 0)

            # -----------------------------------------
            # Deployment Success Logic
            # -----------------------------------------

            risk_score = 0

            if cpu > 85:
                risk_score += 1

            if memory > 85:
                risk_score += 1

            if latency > 700:
                risk_score += 1

            if build_duration > 220:
                risk_score += 1

            if deployment_duration > 90:
                risk_score += 1

            if error_count > 2:
                risk_score += 2

            # Final Label

            if risk_score >= 3:
                deployment_success = 0

            elif risk_score == 2:
                deployment_success = random.choice([0, 1])

            else:
                deployment_success = 1

            # -----------------------------------------
            # Dataset Row
            # -----------------------------------------

            row = {

                "environment_encoded":
                    environment_encoding[environment],

                "cpu_usage": cpu,

                "memory_usage": memory,

                "latency": latency,

                "build_duration": build_duration,

                "deployment_duration": deployment_duration,

                "error_count": error_count,

                "high_cpu": high_cpu,

                "high_memory": high_memory,

                "high_latency": high_latency,

                "deployment_failed": deployment_failed,

                "deployment_success": deployment_success
            }

            data.append(row)

        df = pd.DataFrame(data)

        Path("datasets").mkdir(exist_ok=True)

        df.to_csv(
            DatasetGenerator.OUTPUT_FILE,
            index=False
        )

        print("=" * 60)
        print("DeployGuard AI Dataset Generated Successfully")
        print("=" * 60)

        print("\nFirst 5 Records\n")
        print(df.head())

        print("\nDataset Shape")
        print(df.shape)

        print("\nClass Distribution")
        print(df["deployment_success"].value_counts())

        success_rate = (
            df["deployment_success"].mean() * 100
        )

        print(f"\nDeployment Success Rate : {success_rate:.2f}%")

        print(f"\nDataset saved to: {DatasetGenerator.OUTPUT_FILE}")


if __name__ == "__main__":
    DatasetGenerator.generate()