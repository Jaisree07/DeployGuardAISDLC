import pandas as pd


class FeaturePipeline:

    def run(self):

        df = pd.read_csv("datasets/deployment_dataset.csv")

        df["resource_usage"] = (
            df["cpu_usage"] +
            df["memory_usage"]
        ) / 2

        df["deployment_speed"] = (
            df["build_duration"] +
            df["deployment_duration"]
        ) / 2

        df["failure_risk"] = (
            df["error_count"] * 20
            +
            df["latency"] / 10
        )

        df.to_csv(
            "datasets/ml_dataset.csv",
            index=False
        )

        print("Feature Engineering Completed")


if __name__ == "__main__":

    FeaturePipeline().run()