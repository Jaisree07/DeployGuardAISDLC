import os
import time
import psutil

from backend.monitoring.prometheus import (
    CPU_USAGE,
    MEMORY_USAGE,
    APPLICATION_UPTIME,
)

# Store application start time
START_TIME = time.time()

# Current FastAPI process
process = psutil.Process(os.getpid())


def update_system_metrics():
    """
    Update runtime metrics for DeployGuard API.
    Called on every request by the metrics middleware.
    """

    # CPU usage of this process (%)
    cpu = process.cpu_percent(interval=None)

    # Memory usage of this process (MB)
    memory = process.memory_info().rss / (1024 * 1024)

    # Application uptime (seconds)
    uptime = time.time() - START_TIME

    # Update Prometheus metrics
    CPU_USAGE.set(cpu)
    MEMORY_USAGE.set(memory)
    APPLICATION_UPTIME.set(uptime)