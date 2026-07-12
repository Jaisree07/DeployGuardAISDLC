class SignalParser:

    @staticmethod
    def parse(signal):

        return {
            "deployment_name": signal["deployment_name"],
            "environment": signal["environment"],
            "status": signal["status"],
            "source": signal["source"],
            "timestamp": signal["timestamp"]
        }