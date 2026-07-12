import psutil

from backend.monitoring.prometheus import (
    CPU_USAGE,
    MEMORY_USAGE,
)


def update_system_metrics():
    CPU_USAGE.set(psutil.cpu_percent(interval=0.5))
    MEMORY_USAGE.set(psutil.virtual_memory().percent)