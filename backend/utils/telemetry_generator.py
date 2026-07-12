import random


class TelemetryGenerator:

    @staticmethod
    def generate():
        return {
            "cpu_usage": round(random.uniform(30, 95), 2),
            "memory_usage": round(random.uniform(25, 90), 2),
            "latency": round(random.uniform(50, 350), 2),
            "build_duration": round(random.uniform(40, 200), 2),
            "deployment_duration": round(random.uniform(60, 300), 2),
            "error_count": random.randint(0, 5),
        }