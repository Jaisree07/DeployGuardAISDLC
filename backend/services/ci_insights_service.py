
from collections import defaultdict

from sqlalchemy.orm import Session

from backend.models.ci_event import CIEvent
from backend.ai.ai_service import AIService


CONTROLLED_TEST_BRANCH = "test-ci-failure"


def generate_ci_pipeline_insights(
    db: Session,
    limit: int = 50
) -> dict:
    """
    Generate an AI-powered summary of recent completed CI/CD runs.
    """

    events = (
        db.query(CIEvent)
        .filter(CIEvent.status == "completed")
        .order_by(CIEvent.completed_at.desc())
        .limit(limit)
        .all()
    )

    if not events:
        return {
            "message": "No completed CI/CD pipeline executions found.",
            "metrics": {
                "total_runs": 0,
                "success_count": 0,
                "failure_count": 0,
                "other_count": 0,
                "success_rate": 0,
                "average_duration_seconds": None
            },
            "ai_explanation": None
        }

    success_count = 0
    failure_count = 0
    other_count = 0
    controlled_test_failures = 0
    unexpected_failures = 0

    total_duration = 0
    duration_count = 0

    workflow_stats = defaultdict(
        lambda: {
            "total_runs": 0,
            "success": 0,
            "failure": 0,
            "other": 0,
            "duration_total": 0,
            "duration_count": 0
        }
    )

    failure_details = []

    for event in events:
        conclusion = (event.conclusion or "").lower()
        workflow = workflow_stats[event.workflow_name]

        workflow["total_runs"] += 1

        if conclusion == "success":
            success_count += 1
            workflow["success"] += 1

        elif conclusion == "failure":
            failure_count += 1
            workflow["failure"] += 1

            is_controlled_test = (
                event.branch == CONTROLLED_TEST_BRANCH
            )

            if is_controlled_test:
                controlled_test_failures += 1
            else:
                unexpected_failures += 1

            failure_details.append({
                "workflow": event.workflow_name,
                "branch": event.branch,
                "run_id": event.run_id,
                "controlled_test_failure": is_controlled_test,
                "duration_seconds": event.duration_seconds,
                "run_url": event.html_url
            })

        else:
            other_count += 1
            workflow["other"] += 1

        if event.duration_seconds is not None:
            duration = float(event.duration_seconds)

            total_duration += duration
            duration_count += 1

            workflow["duration_total"] += duration
            workflow["duration_count"] += 1

    total_runs = len(events)

    success_rate = round(
        (success_count / total_runs) * 100,
        2
    )

    average_duration = (
        round(total_duration / duration_count, 2)
        if duration_count
        else None
    )

    workflow_summary = {}

    for workflow_name, stats in workflow_stats.items():
        workflow_summary[workflow_name] = {
            "total_runs": stats["total_runs"],
            "success_count": stats["success"],
            "failure_count": stats["failure"],
            "other_count": stats["other"],
            "average_duration_seconds": (
                round(
                    stats["duration_total"] /
                    stats["duration_count"],
                    2
                )
                if stats["duration_count"]
                else None
            )
        }

    pipeline_data = {
        "total_completed_runs": total_runs,
        "success_count": success_count,
        "failure_count": failure_count,
        "other_count": other_count,
        "success_rate_percent": success_rate,
        "average_duration_seconds": average_duration,
        "controlled_test_failures": controlled_test_failures,
        "unexpected_failures": unexpected_failures,
        "workflow_summary": workflow_summary,
        "failure_details": failure_details
    }

    ai_explanation = AIService.generate_ci_insights(
        pipeline_data
    )

    return {
        "metrics": pipeline_data,
        "ai_explanation": ai_explanation
    }
