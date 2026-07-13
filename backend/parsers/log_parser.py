import re
from pathlib import Path
from collections import Counter


class LogParser:

    LOG_FILE = "logs/deployguard.log"

    @staticmethod
    def parse():

        path = Path(LogParser.LOG_FILE)

        if not path.exists():

            return {
                "status": "NO_LOG_FILE",
                "total_lines": 0,
                "errors": 0,
                "warnings": 0,
                "info": 0,
                "exceptions": 0
            }

        text = path.read_text(encoding="utf-8")

        lines = text.splitlines()

        counts = Counter()

        for line in lines:

            if "ERROR" in line:
                counts["errors"] += 1

            if "WARNING" in line:
                counts["warnings"] += 1

            if "INFO" in line:
                counts["info"] += 1

            if "Exception" in line or "Traceback" in line:
                counts["exceptions"] += 1

        status = "FAILED" if counts["errors"] else "SUCCESS"

        return {

            "status": status,

            "total_lines": len(lines),

            "errors": counts["errors"],

            "warnings": counts["warnings"],

            "info": counts["info"],

            "exceptions": counts["exceptions"]

        }


if __name__ == "__main__":

    print(LogParser.parse())