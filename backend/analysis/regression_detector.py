from sqlalchemy.orm import Session

from backend.models.deployment import Deployment
from backend.models.telemetry import Telemetry


# ============================================================
# COMMON HELPERS
# ============================================================

def _recent_deployments(
    db: Session,
    environment: str,
    limit: int = 10
):
    return (
        db.query(Deployment)
        .filter(
            Deployment.environment == environment
        )
        .order_by(
            Deployment.id.desc()
        )
        .limit(limit)
        .all()
    )


def _get_telemetry(
    db: Session,
    deployment_id: int
):
    return (
        db.query(Telemetry)
        .filter(
            Telemetry.deployment_id == deployment_id
        )
        .order_by(
            Telemetry.id.desc()
        )
        .first()
    )


def _baseline_average(
    db: Session,
    deployments,
    attribute: str
):
    values = []

    for deployment in deployments:

        telemetry = _get_telemetry(
            db,
            deployment.id
        )

        if telemetry is None:
            continue

        value = getattr(
            telemetry,
            attribute,
            None
        )

        if value is not None:
            values.append(value)

    if not values:
        return None, 0

    return (
        sum(values) / len(values),
        len(values)
    )


# ============================================================
# 1. DEPLOYMENT PERFORMANCE REGRESSION
# ============================================================

def detect_performance_regression(
    db: Session,
    environment: str
):
    deployments = _recent_deployments(
        db,
        environment,
        limit=10
    )

    if len(deployments) < 4:
        return None

    latest = deployments[0]

    baseline_deployments = deployments[1:]

    latest_telemetry = _get_telemetry(
        db,
        latest.id
    )

    if (
        latest_telemetry is None
        or latest_telemetry.deployment_duration is None
    ):
        return None

    baseline_avg, sample_size = _baseline_average(
        db,
        baseline_deployments,
        "deployment_duration"
    )

    if baseline_avg is None or baseline_avg <= 0:
        return None

    pct_increase = (
        (
            latest_telemetry.deployment_duration
            - baseline_avg
        )
        / baseline_avg
    ) * 100

    if pct_increase < 30:
        return None

    return {
        "pattern": "performance_regression",
        "environment": environment,
        "deployment_id": latest.id,
        "deployment_name": latest.deployment_name,
        "version": latest.version,
        "latest_duration": round(
            latest_telemetry.deployment_duration,
            2
        ),
        "baseline_avg_duration": round(
            baseline_avg,
            2
        ),
        "pct_increase": round(
            pct_increase,
            1
        ),
        "sample_size": sample_size,
        "severity": (
            "HIGH"
            if pct_increase >= 50
            else "MEDIUM"
        )
    }


# ============================================================
# 2. DEPLOYMENT RELIABILITY REGRESSION
# ============================================================

def detect_reliability_regression(
    db: Session,
    environment: str
):
    deployments = _recent_deployments(
        db,
        environment,
        limit=10
    )

    if len(deployments) < 4:
        return None

    latest_batch = deployments[:3]

    baseline_batch = deployments[3:]

    def fail_rate(batch):

        if not batch:
            return None

        failed = sum(
            1
            for deployment in batch
            if deployment.status.upper()
            not in (
                "SUCCESS",
                "RUNNING",
                "COMPLETED",
                "VERIFIED"
            )
        )

        return failed / len(batch)

    latest_rate = fail_rate(
        latest_batch
    )

    baseline_rate = fail_rate(
        baseline_batch
    )

    if (
        latest_rate is None
        or baseline_rate is None
    ):
        return None

    increase = (
        latest_rate
        - baseline_rate
    )

    if increase < 0.34:
        return None

    return {
        "pattern": "reliability_regression",
        "environment": environment,
        "deployment_id": latest_batch[0].id,
        "deployment_name": (
            latest_batch[0].deployment_name
        ),
        "version": latest_batch[0].version,
        "latest_failure_rate_pct": round(
            latest_rate * 100,
            1
        ),
        "baseline_failure_rate_pct": round(
            baseline_rate * 100,
            1
        ),
        "increase_pct": round(
            increase * 100,
            1
        ),
        "recent_statuses": [
            deployment.status
            for deployment in latest_batch
        ],
        "severity": "HIGH"
    }


# ============================================================
# 3. CPU USAGE REGRESSION
# ============================================================

def detect_cpu_regression(
    db: Session,
    environment: str
):
    deployments = _recent_deployments(
        db,
        environment,
        limit=10
    )

    if len(deployments) < 4:
        return None

    latest = deployments[0]

    baseline_deployments = deployments[1:]

    latest_telemetry = _get_telemetry(
        db,
        latest.id
    )

    if (
        latest_telemetry is None
        or latest_telemetry.cpu_usage is None
    ):
        return None

    baseline_avg, sample_size = _baseline_average(
        db,
        baseline_deployments,
        "cpu_usage"
    )

    if baseline_avg is None or baseline_avg <= 0:
        return None

    pct_increase = (
        (
            latest_telemetry.cpu_usage
            - baseline_avg
        )
        / baseline_avg
    ) * 100

    if pct_increase < 30:
        return None

    return {
        "pattern": "cpu_usage_regression",
        "environment": environment,
        "deployment_id": latest.id,
        "deployment_name": latest.deployment_name,
        "version": latest.version,
        "latest_cpu_usage": round(
            latest_telemetry.cpu_usage,
            2
        ),
        "baseline_avg_cpu_usage": round(
            baseline_avg,
            2
        ),
        "pct_increase": round(
            pct_increase,
            1
        ),
        "sample_size": sample_size,
        "severity": (
            "HIGH"
            if pct_increase >= 50
            else "MEDIUM"
        )
    }


# ============================================================
# 4. MEMORY USAGE REGRESSION
# ============================================================

def detect_memory_regression(
    db: Session,
    environment: str
):
    deployments = _recent_deployments(
        db,
        environment,
        limit=10
    )

    if len(deployments) < 4:
        return None

    latest = deployments[0]

    baseline_deployments = deployments[1:]

    latest_telemetry = _get_telemetry(
        db,
        latest.id
    )

    if (
        latest_telemetry is None
        or latest_telemetry.memory_usage is None
    ):
        return None

    baseline_avg, sample_size = _baseline_average(
        db,
        baseline_deployments,
        "memory_usage"
    )

    if baseline_avg is None or baseline_avg <= 0:
        return None

    pct_increase = (
        (
            latest_telemetry.memory_usage
            - baseline_avg
        )
        / baseline_avg
    ) * 100

    if pct_increase < 30:
        return None

    return {
        "pattern": "memory_usage_regression",
        "environment": environment,
        "deployment_id": latest.id,
        "deployment_name": latest.deployment_name,
        "version": latest.version,
        "latest_memory_usage": round(
            latest_telemetry.memory_usage,
            2
        ),
        "baseline_avg_memory_usage": round(
            baseline_avg,
            2
        ),
        "pct_increase": round(
            pct_increase,
            1
        ),
        "sample_size": sample_size,
        "severity": (
            "HIGH"
            if pct_increase >= 50
            else "MEDIUM"
        )
    }


# ============================================================
# 5. LATENCY REGRESSION
# ============================================================

def detect_latency_regression(
    db: Session,
    environment: str
):
    deployments = _recent_deployments(
        db,
        environment,
        limit=10
    )

    if len(deployments) < 4:
        return None

    latest = deployments[0]

    baseline_deployments = deployments[1:]

    latest_telemetry = _get_telemetry(
        db,
        latest.id
    )

    if (
        latest_telemetry is None
        or latest_telemetry.latency is None
    ):
        return None

    baseline_avg, sample_size = _baseline_average(
        db,
        baseline_deployments,
        "latency"
    )

    if baseline_avg is None or baseline_avg <= 0:
        return None

    pct_increase = (
        (
            latest_telemetry.latency
            - baseline_avg
        )
        / baseline_avg
    ) * 100

    if pct_increase < 30:
        return None

    return {
        "pattern": "latency_regression",
        "environment": environment,
        "deployment_id": latest.id,
        "deployment_name": latest.deployment_name,
        "version": latest.version,
        "latest_latency": round(
            latest_telemetry.latency,
            2
        ),
        "baseline_avg_latency": round(
            baseline_avg,
            2
        ),
        "pct_increase": round(
            pct_increase,
            1
        ),
        "sample_size": sample_size,
        "severity": (
            "HIGH"
            if pct_increase >= 50
            else "MEDIUM"
        )
    }


# ============================================================
# 6. REGRESSION HISTORY
# ============================================================

def get_regression_history(
    db: Session,
    environment: str,
    limit: int = 20
):
    """
    Build historical deployment regression
    information for Grafana and API consumers.
    """

    deployments = _recent_deployments(
        db,
        environment,
        limit=limit
    )

    if not deployments:
        return []

    history = []

    for index, deployment in enumerate(
        deployments
    ):

        telemetry = _get_telemetry(
            db,
            deployment.id
        )

        if telemetry is None:
            continue

        previous_deployments = deployments[
            index + 1:
        ]

        baseline_durations = []

        for previous_deployment in previous_deployments:

            previous_telemetry = _get_telemetry(
                db,
                previous_deployment.id
            )

            if (
                previous_telemetry is not None
                and previous_telemetry.deployment_duration
                is not None
            ):
                baseline_durations.append(
                    previous_telemetry.deployment_duration
                )

        regression_percent = 0.0
        baseline_average = None

        if baseline_durations:

            baseline_average = (
                sum(baseline_durations)
                / len(baseline_durations)
            )

            if baseline_average > 0:

                regression_percent = (
                    (
                        telemetry.deployment_duration
                        - baseline_average
                    )
                    / baseline_average
                ) * 100

        is_regression = (
            regression_percent >= 30
        )

        history.append(
            {
                "deployment_id": deployment.id,
                "deployment_name": (
                    deployment.deployment_name
                ),
                "version": deployment.version,
                "environment": (
                    deployment.environment
                ),
                "status": deployment.status,
                "deployment_duration": round(
                    telemetry.deployment_duration,
                    2
                ),
                "build_duration": round(
                    telemetry.build_duration,
                    2
                ),
                "cpu_usage": round(
                    telemetry.cpu_usage,
                    2
                ),
                "memory_usage": round(
                    telemetry.memory_usage,
                    2
                ),
                "latency": round(
                    telemetry.latency,
                    2
                ),
                "error_count": (
                    telemetry.error_count
                ),
                "baseline_average_duration": (
                    round(
                        baseline_average,
                        2
                    )
                    if baseline_average is not None
                    else None
                ),
                "regression_percent": round(
                    regression_percent,
                    1
                ),
                "regression_detected": (
                    is_regression
                ),
                "severity": (
                    "HIGH"
                    if regression_percent >= 50
                    else "MEDIUM"
                    if is_regression
                    else "NORMAL"
                ),
                "collected_at": (
                    telemetry.collected_at.isoformat()
                    if telemetry.collected_at
                    else None
                )
            }
        )

    return history


# ============================================================
# 7. DETECT ALL REGRESSION PATTERNS
# ============================================================

def detect_all_patterns(
    db: Session,
    environment: str
):
    patterns = []

    # Performance
    performance = detect_performance_regression(
        db,
        environment
    )

    if performance:
        patterns.append(
            performance
        )

    # Reliability
    reliability = detect_reliability_regression(
        db,
        environment
    )

    if reliability:
        patterns.append(
            reliability
        )

    # CPU
    cpu = detect_cpu_regression(
        db,
        environment
    )

    if cpu:
        patterns.append(
            cpu
        )

    # Memory
    memory = detect_memory_regression(
        db,
        environment
    )

    if memory:
        patterns.append(
            memory
        )

    # Latency
    latency = detect_latency_regression(
        db,
        environment
    )

    if latency:
        patterns.append(
            latency
        )

    return patterns