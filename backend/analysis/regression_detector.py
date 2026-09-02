from sqlalchemy.orm import Session

from backend.models.deployment import Deployment
from backend.models.telemetry import Telemetry


def _recent_deployments(
    db: Session,
    environment: str,
    limit: int = 10
):
    return (
        db.query(Deployment)
        .filter(Deployment.environment == environment)
        .order_by(Deployment.id.desc())
        .limit(limit)
        .all()
    )


def _get_telemetry(db: Session, deployment_id: int):
    return (
        db.query(Telemetry)
        .filter(Telemetry.deployment_id == deployment_id)
        .order_by(Telemetry.id.desc())
        .first()
    )


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
    baseline = deployments[1:]

    latest_t = _get_telemetry(db, latest.id)

    if not latest_t or latest_t.deployment_duration is None:
        return None

    baseline_durations = []

    for deployment in baseline:
        telemetry = _get_telemetry(
            db,
            deployment.id
        )

        if (
            telemetry
            and telemetry.deployment_duration is not None
        ):
            baseline_durations.append(
                telemetry.deployment_duration
            )

    if not baseline_durations:
        return None

    avg_baseline = (
        sum(baseline_durations)
        / len(baseline_durations)
    )

    if avg_baseline == 0:
        return None

    pct_increase = (
        (
            latest_t.deployment_duration
            - avg_baseline
        )
        / avg_baseline
    ) * 100

    if pct_increase >= 30:
        return {
            "pattern": "performance_regression",
            "environment": environment,
            "deployment_id": latest.id,
            "deployment_name": latest.deployment_name,
            "version": latest.version,
            "latest_duration": round(
                latest_t.deployment_duration,
                2
            ),
            "baseline_avg_duration": round(
                avg_baseline,
                2
            ),
            "pct_increase": round(
                pct_increase,
                1
            ),
            "sample_size": len(
                baseline_durations
            ),
            "severity": (
                "HIGH"
                if pct_increase >= 50
                else "MEDIUM"
            )
        }

    return None


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

    if increase >= 0.34:
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

    return None


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

        if not telemetry:
            continue

        # Previous deployments are used
        # as the baseline for this deployment.
        previous = deployments[index + 1:]

        baseline_durations = []

        for previous_deployment in previous:
            previous_telemetry = _get_telemetry(
                db,
                previous_deployment.id
            )

            if (
                previous_telemetry
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
                "error_count": telemetry.error_count,
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


def detect_all_patterns(
    db: Session,
    environment: str
):
    patterns = []

    performance = detect_performance_regression(
        db,
        environment
    )

    if performance:
        patterns.append(performance)

    reliability = detect_reliability_regression(
        db,
        environment
    )

    if reliability:
        patterns.append(reliability)

    return patterns