from sqlalchemy.orm import Session

from backend.models.deployment import Deployment
from backend.models.telemetry import Telemetry
from backend.models.prediction import Prediction

from backend.prediction.predictor import Predictor

from backend.analysis.regression_detector import (
    detect_all_patterns,
)

from backend.monitoring.prometheus import (
    DEPLOYMENT_INFO,
    DEPLOYMENT_RISK,
    REGRESSION_DETECTED,
)


class VerificationService:

    @staticmethod
    def _risk_value(risk: str) -> int:
        """
        Convert ML risk level into a numeric value
        for Prometheus/Grafana.

        0 = Low
        1 = Medium
        2 = High / Critical
        """

        risk = str(risk).upper()

        if risk == "LOW":
            return 0

        if risk == "MEDIUM":
            return 1

        if risk in ("HIGH", "CRITICAL"):
            return 2

        return 1

    @staticmethod
    def _publish_dashboard_metrics(
        deployment,
        prediction_result,
        deployment_regressions
    ):
        """
        Publish per-deployment metrics used by Grafana.

        Metrics:
        1. Deployment History
        2. Predicted Risk per Deployment
        3. Regression Timeline
        """

        deployment_id = str(deployment.id)
        deployment_name = str(deployment.deployment_name)
        version = str(deployment.version)
        environment = str(deployment.environment)
        status = str(deployment.status)

        # ---------------------------------------------------------
        # Deployment History
        # ---------------------------------------------------------

        for old_status in (
            "CREATED",
            "RUNNING",
            "SUCCESS",
            "COMPLETED",
            "VERIFIED",
            "BLOCKED",
            "FAILED",
        ):
            try:
                DEPLOYMENT_INFO.remove(
                    deployment_id,
                    deployment_name,
                    version,
                    environment,
                    old_status,
                )
            except KeyError:
                pass

        DEPLOYMENT_INFO.labels(
            deployment_id=deployment_id,
            deployment_name=deployment_name,
            version=version,
            environment=environment,
            status=status,
        ).set(1)

        # ---------------------------------------------------------
        # Predicted Risk
        # ---------------------------------------------------------

        risk = prediction_result.get(
            "risk",
            "MEDIUM"
        )

        risk_value = VerificationService._risk_value(
            risk
        )

        DEPLOYMENT_RISK.labels(
            deployment_id=deployment_id,
            deployment_name=deployment_name,
            environment=environment,
        ).set(risk_value)

        # ---------------------------------------------------------
        # Regression Timeline
        # ---------------------------------------------------------

        regression_patterns = (
            "performance_regression",
            "reliability_regression",
            "cpu_usage_regression",
            "memory_usage_regression",
            "latency_regression",
        )

        severities = (
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL",
        )

        for pattern in regression_patterns:
            for severity in severities:
                try:
                    REGRESSION_DETECTED.remove(
                        deployment_id,
                        deployment_name,
                        environment,
                        pattern,
                        severity,
                    )
                except KeyError:
                    pass

        for regression in deployment_regressions:

            pattern = str(
                regression.get(
                    "pattern",
                    "unknown_regression"
                )
            )

            severity = str(
                regression.get(
                    "severity",
                    "MEDIUM"
                )
            ).upper()

            REGRESSION_DETECTED.labels(
                deployment_id=deployment_id,
                deployment_name=deployment_name,
                environment=environment,
                pattern=pattern,
                severity=severity,
            ).set(1)

    @staticmethod
    def _save_prediction(
        db: Session,
        deployment_id: int,
        prediction_result: dict
    ):
        """
        Persist the ML prediction and real AI explanation
        for the verified deployment.
        """

        prediction_record = Prediction(
            deployment_id=deployment_id,

            prediction=prediction_result.get(
                "prediction",
                ""
            ),

            confidence=prediction_result.get(
                "confidence",
                0
            ),

            anomaly=str(
                prediction_result.get(
                    "anomaly",
                    "No"
                )
            ),

            risk=prediction_result.get(
                "risk",
                "MEDIUM"
            ),

            ai_explanation=prediction_result.get(
                "ai_explanation",
                ""
            ),
        )

        db.add(prediction_record)
        db.commit()
        db.refresh(prediction_record)

        return prediction_record

    @staticmethod
    def verify(
        db: Session,
        deployment_id: int
    ):

        # ---------------------------------------------------------
        # Get Deployment
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # Get Latest Telemetry
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # Prepare ML Input
        # ---------------------------------------------------------

        prediction_input = {
            "environment": deployment.environment,

            "cpu_usage": telemetry.cpu_usage,

            "memory_usage": telemetry.memory_usage,

            "latency": telemetry.latency,

            "build_duration": telemetry.build_duration,

            "deployment_duration": telemetry.deployment_duration,

            "error_count": telemetry.error_count,
        }

        # ---------------------------------------------------------
        # ML + Anomaly Detection + AI Explanation
        # ---------------------------------------------------------

        prediction_result = Predictor.predict(
            prediction_input
        )

        # ---------------------------------------------------------
        # Regression Detection
        # ---------------------------------------------------------

        regression_patterns = detect_all_patterns(
            db,
            deployment.environment
        )

        deployment_regressions = [
            pattern
            for pattern in regression_patterns
            if pattern.get("deployment_id")
            == deployment_id
        ]

        # ---------------------------------------------------------
        # Extract Prediction Results
        # ---------------------------------------------------------

        risk = prediction_result.get(
            "risk",
            ""
        )

        anomaly = prediction_result.get(
            "anomaly",
            "No"
        )

        ai_explanation = prediction_result.get(
            "ai_explanation",
            ""
        )

        # ---------------------------------------------------------
        # Verification Decision
        # ---------------------------------------------------------

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

        deployment.status = decision

        # ---------------------------------------------------------
        # Save Deployment
        # ---------------------------------------------------------

        db.commit()
        db.refresh(deployment)

        # ---------------------------------------------------------
        # Save ML + AI Prediction
        # ---------------------------------------------------------

        prediction_record = VerificationService._save_prediction(
            db=db,
            deployment_id=deployment_id,
            prediction_result=prediction_result,
        )

        # ---------------------------------------------------------
        # Publish Prometheus Metrics
        # ---------------------------------------------------------

        VerificationService._publish_dashboard_metrics(
            deployment=deployment,
            prediction_result=prediction_result,
            deployment_regressions=deployment_regressions,
        )

        # ---------------------------------------------------------
        # Return Complete Verification Result
        # ---------------------------------------------------------

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

            "prediction_record_id": prediction_record.id,

            "regressions": deployment_regressions,

            "regression_count": len(
                deployment_regressions
            ),

            "blocked_reasons": blocked_reasons,

            "ai_analysis": {
                "available": bool(ai_explanation),

                "explanation": ai_explanation,
            },
        }