from datetime import datetime


class SignalCollector:

    @staticmethod
    def collect(
        deployment_name,
        environment,
        status,
        source="FastAPI"
    ):

        return {
            "deployment_name": deployment_name,
            "environment": environment,
            "status": status,
            "source": source,
            "timestamp": datetime.utcnow().isoformat()
        }