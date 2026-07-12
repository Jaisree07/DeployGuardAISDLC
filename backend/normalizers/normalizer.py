class SignalNormalizer:

    STATUS_MAP = {
    "Running": "SUCCESS",
    "Healthy": "SUCCESS",
    "Succeeded": "SUCCESS",
    "success": "SUCCESS",

    "Stopped": "FAILED",
    "failure": "FAILED",
    "Failed": "FAILED",
    "Degraded": "FAILED",

    "Progressing": "IN_PROGRESS",
    "Pending": "IN_PROGRESS",

    "Unknown": "UNKNOWN"
}

    @staticmethod
    def normalize(signal):

        signal["status"] = SignalNormalizer.STATUS_MAP.get(
            signal["status"],
            signal["status"]
        )

        return signal