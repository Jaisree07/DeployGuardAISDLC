from sqlalchemy.orm import Session

from backend.models.deployment import Deployment
from backend.models.telemetry import Telemetry

from backend.prediction.predictor import Predictor

from backend.analysis.regression_detector import (
    detect_all_patterns,
)


class VerificationService:

    @staticmethod
    def verify(
        db: Session,
        deployment_id: int
    ):
        # =====================================================
        # 1. Get Deployment
        # =====================================================

        deployment = (
            db.query(Deployment)
            .filter(
                Deployment.id == deployment_id
            )
            .first()
        )

        if deployment is None:
            raise ValueError(
                "Deployment not found"
            )

        # =====================================================
        # 2. Get Latest Telemetry
        # =====================================================

        telemetry = (
            db.query(Telemetry)
            .filter(
                Telemetry.deployment_id
                == deployment_id
            )
            .order_by(
                Telemetry.id.desc()
            )
            .first()
        )

        if telemetry is None:
            raise ValueError(
                "Telemetry not found for deployment"
            )

        # =====================================================
        # 3. Prepare Actual Telemetry for ML
        # =====================================================

        prediction_input = {
            "environment": deployment.environment,
            "cpu_usage": telemetry.cpu_usage,
            "memory_usage": telemetry.memory_usage,
            "latency": telemetry.latency,
            "build_duration": telemetry.build_duration,
            "deployment_duration": telemetry.deployment_duration,
            "error_count": telemetry.error_count,
        }

        # =====================================================
        # 4. Run Existing ML + Anomaly + AI
        # =====================================================

        prediction_result = Predictor.predict(
            prediction_input
        )

        # =====================================================
        # 5. Run Existing Regression Detection
        # =====================================================

        regression_patterns = detect_all_patterns(
            db,
            deployment.environment
        )

        # Only consider regression patterns
        # belonging to the deployment being verified.

        deployment_regressions = [
            pattern
            for pattern in regression_patterns
            if pattern.get("deployment_id")
            == deployment_id
        ]

        # =====================================================
        # 6. Determine Verification Decision
        # =====================================================

        risk = prediction_result.get(
            "risk",
            ""
        )

        anomaly = prediction_result.get(
            "anomaly",
            "No"
        )

        blocked_reasons = []

        if risk.upper() in (
            "CRITICAL",
            "HIGH"
        ):
            blocked_reasons.append(
                "High or critical ML risk detected"
            )

        if str(anomaly).lower() not in (
            "no",
            "normal",
            "0",
            "false"
        ):
            blocked_reasons.append(
                "Deployment anomaly detected"
            )

        if deployment_regressions:
            blocked_reasons.append(
                "Performance or reliability regression detected"
            )

        if blocked_reasons:
            decision = "BLOCKED"
        else:
            decision = "VERIFIED"

        # =====================================================
        # 7. Update Deployment Status
        # =====================================================

        deployment.status = decision

        db.commit()
        db.refresh(deployment)

        # =====================================================
        # 8. Return Complete Verification Result
        # =====================================================

        return {
            "success": True,
            "deployment_id": deployment.id,
            "deployment_name": deployment.deployment_name,
            "version": deployment.version,
            "environment": deployment.environment,
            "verification": decision,
            "deployment_status": deployment.status,
            "telemetry": {
                "cpu_usage": telemetry.cpu_usage,
                "memory_usage": telemetry.memory_usage,
                "latency": telemetry.latency,
                "build_duration": telemetry.build_duration,
                "deployment_duration": telemetry.deployment_duration,
                "error_count": telemetry.error_count,
            },
            "ml_prediction": prediction_result,
            "regressions": deployment_regressions,
            "regression_count": len(
                deployment_regressions
            ),
            "blocked_reasons": blocked_reasons,
        }
