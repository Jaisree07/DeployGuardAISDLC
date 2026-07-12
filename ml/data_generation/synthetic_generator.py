import random
import pandas as pd
from faker import Faker

fake = Faker()


class SyntheticDeploymentGenerator:

    ENVIRONMENTS = ["DEV", "QA", "UAT", "PROD"]

    STATUS = [
        "Success",
        "Failed",
        "Running"
    ]

    def generate(self, rows=5000):

        data = []

        for deployment_id in range(1, rows + 1):

            cpu = round(random.uniform(20, 100), 2)

            memory = round(random.uniform(20, 100), 2)

            latency = round(random.uniform(20, 400), 2)

            build_duration = round(random.uniform(30, 300), 2)

            deployment_duration = round(random.uniform(40, 350), 2)

            error_count = random.randint(0, 5)

            healthy = (
                error_count == 0
                and cpu < 85
                and memory < 85
                and latency < 250
            )

            data.append({

                "deployment_id": deployment_id,

                "deployment_name": fake.word().capitalize() + "-Service",

                "version": f"1.{random.randint(0,9)}.{random.randint(0,9)}",

                "environment": random.choice(self.ENVIRONMENTS),

                "status": random.choice(self.STATUS),

                "cpu_usage": cpu,

                "memory_usage": memory,

                "latency": latency,

                "build_duration": build_duration,

                "deployment_duration": deployment_duration,

                "error_count": error_count,

                "healthy": int(healthy)

            })

        df = pd.DataFrame(data)

        df.to_csv(
            "datasets/deployment_dataset.csv",
            index=False
        )

        print(df.head())

        print(f"\nGenerated {len(df)} records.")


if __name__ == "__main__":

    SyntheticDeploymentGenerator().generate()