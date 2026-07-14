from sqlalchemy.orm import Session
from backend.models.deployment import Deployment
from backend.models.telemetry import Telemetry


def _recent_deployments(db: Session, environment: str, limit: int = 10):
    return (
        db.query(Deployment)
        .filter(Deployment.environment == environment)
        .order_by(Deployment.id.desc())
        .limit(limit)
        .all()
    )


def detect_performance_regression(db: Session, environment: str):
    deployments = _recent_deployments(db, environment, limit=10)
    if len(deployments) < 4:
        return None

    latest = deployments[0]
    baseline = deployments[1:]

    latest_t = db.query(Telemetry).filter(
        Telemetry.deployment_id == latest.id
    ).first()
    if not latest_t or latest_t.deployment_duration is None:
        return None

    baseline_durations = []
    for d in baseline:
        t = db.query(Telemetry).filter(Telemetry.deployment_id == d.id).first()
        if t and t.deployment_duration is not None:
            baseline_durations.append(t.deployment_duration)

    if not baseline_durations:
        return None

    avg_baseline = sum(baseline_durations) / len(baseline_durations)
    if avg_baseline == 0:
        return None

    pct_increase = ((latest_t.deployment_duration - avg_baseline) / avg_baseline) * 100

    if pct_increase >= 30:
        return {
            "pattern": "performance_regression",
            "environment": environment,
            "deployment_name": latest.deployment_name,
            "latest_duration": round(latest_t.deployment_duration, 2),
            "baseline_avg_duration": round(avg_baseline, 2),
            "pct_increase": round(pct_increase, 1),
            "sample_size": len(baseline_durations),
        }
    return None


def detect_reliability_regression(db: Session, environment: str):
    deployments = _recent_deployments(db, environment, limit=10)
    if len(deployments) < 4:
        return None

    latest_batch = deployments[:3]
    baseline_batch = deployments[3:]

    def fail_rate(batch):
        if not batch:
            return None
        failed = sum(1 for d in batch if d.status not in ("SUCCESS", "Running"))
        return failed / len(batch)

    latest_rate = fail_rate(latest_batch)
    baseline_rate = fail_rate(baseline_batch)

    if latest_rate is None or baseline_rate is None:
        return None

    if latest_rate - baseline_rate >= 0.34:
        return {
            "pattern": "reliability_regression",
            "environment": environment,
            "deployment_name": latest_batch[0].deployment_name,
            "latest_failure_rate_pct": round(latest_rate * 100, 1),
            "baseline_failure_rate_pct": round(baseline_rate * 100, 1),
            "recent_statuses": [d.status for d in latest_batch],
        }
    return None


def detect_all_patterns(db: Session, environment: str):
    patterns = []
    for detector in (detect_performance_regression, detect_reliability_regression):
        result = detector(db, environment)
        if result:
            patterns.append(result)
    return patterns
