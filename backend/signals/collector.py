from datetime import datetime

from backend.signals.argocd import ArgoCDCollector


class SignalCollector:

    @staticmethod
    def collect(
        deployment_name,
        environment,
        status,
        source="FastAPI"
    ):

        # Collect Argo CD deployment information
        argocd_signal = ArgoCDCollector.collect()

        return {

            "deployment_name": deployment_name,

            "environment": environment,

            "status": status,

            "source": source,

            "timestamp": datetime.utcnow().isoformat(),

            # Argo CD Deployment Information
            "argocd": argocd_signal

        }