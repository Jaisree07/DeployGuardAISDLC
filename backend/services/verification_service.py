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

    # Deployment counters
    DEPLOYMENT_SUCCESS,
    DEPLOYMENT_FAILURE,

    # Prediction counters
    PREDICTION_COUNT,
    PREDICTION_SUCCESS,
    PREDICTION_FAILURE,

    # Deployment intelligence
    PREDICTED_RISK,
    ANOMALY_DETECTED,
)


class VerificationService:

    # =====================================================
    # Risk Conversion
    # =====================================================

    @staticmethod
    def _risk_value(risk: str) -> int:
        risk = str(risk).upper()

        if risk == "LOW":
            return 0

        if risk == "MEDIUM":
            return 1

        if risk in (
            "HIGH",
            "CRITICAL"
        ):
            return 2

        return 1


    # =====================================================
    # Publish Dashboard Metrics
    # =====================================================

    @staticmethod
    def _publish_dashboard_metrics(
        deployment,
        prediction_result,
        deployment_regressions
    ):

        deployment_id = str(
            deployment.id
        )

        deployment_name = str(
            deployment.deployment_name
        )

        version = str(
            deployment.version
        )

        environment = str(
            deployment.environment
        )

        status = str(
            deployment.status
        ).upper()


        # -------------------------------------------------
        # Deployment Information
        # -------------------------------------------------

        old_statuses = (
            "CREATED",
            "RUNNING",
            "SUCCESS",
            "COMPLETED",
            "VERIFIED",
            "BLOCKED",
            "FAILED",
        )

        for old_status in old_statuses:

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


        # -------------------------------------------------
        # Per Deployment Risk
        # -------------------------------------------------

        risk = prediction_result.get(
            "risk",
            "MEDIUM"
        )

        risk_value = (
            VerificationService._risk_value(
                risk
            )
        )

        DEPLOYMENT_RISK.labels(
            deployment_id=deployment_id,
            deployment_name=deployment_name,
            environment=environment,
        ).set(
            risk_value
        )


        # -------------------------------------------------
        # Remove Previous Regression Labels
        # -------------------------------------------------

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


        # -------------------------------------------------
        # Publish Current Regressions
        # -------------------------------------------------

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


    # =====================================================
    # Save Prediction
    # =====================================================

    @staticmethod
    def _save_prediction(
        db: Session,
        deployment_id: int,
        prediction_result: dict
    ):

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


        db.add(
            prediction_record
        )

        db.commit()

        db.refresh(
            prediction_record
        )

        return prediction_record


    # =====================================================
    # Main Verification
    # =====================================================

    @staticmethod
    def verify(
        db: Session,
        deployment_id: int
    ):

        # -------------------------------------------------
        # Find Deployment
        # -------------------------------------------------

        deployment = (
            db.query(Deployment)
            .filter(
                Deployment.id
                == deployment_id
            )
            .first()
        )


        if deployment is None:

            raise ValueError(
                "Deployment not found"
            )


        # -------------------------------------------------
        # Find Latest Telemetry
        # -------------------------------------------------

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


        # -------------------------------------------------
        # Prepare ML Input
        # -------------------------------------------------

        prediction_input = {

            "environment":
                deployment.environment,

            "cpu_usage":
                telemetry.cpu_usage,

            "memory_usage":
                telemetry.memory_usage,

            "latency":
                telemetry.latency,

            "build_duration":
                telemetry.build_duration,

            "deployment_duration":
                telemetry.deployment_duration,

            "error_count":
                telemetry.error_count,
        }


        # -------------------------------------------------
        # Run ML + Anomaly + AI
        # -------------------------------------------------

        prediction_result = (
            Predictor.predict(
                prediction_input
            )
        )


        # =================================================
        # PROMETHEUS — Prediction Metrics
        # =================================================

        PREDICTION_COUNT.inc()


        prediction_status = str(
            prediction_result.get(
                "prediction",
                ""
            )
        ).strip().lower()


        if prediction_status == (
            "healthy deployment"
        ):

            PREDICTION_SUCCESS.inc()

        else:

            PREDICTION_FAILURE.inc()


        # =================================================
        # Regression Detection
        # =================================================

        regression_patterns = (
            detect_all_patterns(
                db,
                deployment.environment
            )
        )


        deployment_regressions = [

            pattern

            for pattern
            in regression_patterns

            if pattern.get(
                "deployment_id"
            ) == deployment_id
        ]


        # =================================================
        # Extract ML Results
        # =================================================

        risk = prediction_result.get(
            "risk",
            "MEDIUM"
        )


        anomaly = prediction_result.get(
            "anomaly",
            "No"
        )


        ai_explanation = (
            prediction_result.get(
                "ai_explanation",
                ""
            )
        )


        # =================================================
        # PROMETHEUS — Global Risk
        # =================================================

        risk_upper = str(
            risk
        ).upper()


        if risk_upper == "LOW":

            PREDICTED_RISK.set(0)

        elif risk_upper == "MEDIUM":

            PREDICTED_RISK.set(1)

        elif risk_upper in (
            "HIGH",
            "CRITICAL"
        ):

            PREDICTED_RISK.set(2)

        else:

            PREDICTED_RISK.set(1)


        # =================================================
        # PROMETHEUS — Anomaly
        # =================================================

        anomaly_value = str(
            anomaly
        ).strip().lower()


        if anomaly_value in (
            "yes",
            "true",
            "1",
            "anomaly"
        ):

            ANOMALY_DETECTED.set(1)

        else:

            ANOMALY_DETECTED.set(0)


        # =================================================
        # Determine Verification Decision
        # =================================================

        blocked_reasons = []


        # -------------------------------------------------
        # ML Risk Gate
        # -------------------------------------------------

        if risk_upper in (
            "CRITICAL",
            "HIGH"
        ):

            blocked_reasons.append(
                "High or critical ML risk detected"
            )


        # -------------------------------------------------
        # Anomaly Gate
        # -------------------------------------------------

        if anomaly_value not in (
            "no",
            "normal",
            "0",
            "false"
        ):

            blocked_reasons.append(
                "Deployment anomaly detected"
            )


        # -------------------------------------------------
        # Regression Gate
        # -------------------------------------------------

        if deployment_regressions:

            blocked_reasons.append(
                "Performance or reliability regression detected"
            )


        # -------------------------------------------------
        # Final Decision
        # -------------------------------------------------

        if blocked_reasons:

            decision = "BLOCKED"

        else:

            decision = "VERIFIED"


        # =================================================
        # Save Deployment Status
        # =================================================

        previous_status = str(
            deployment.status
        ).upper()


        deployment.status = decision


        db.commit()


        db.refresh(
            deployment
        )


        # =================================================
        # PROMETHEUS — Deployment Outcome
        #
        # Count only when transitioning from a
        # non-terminal state to a terminal state.
        # This prevents duplicate verification calls
        # from inflating the dashboard.
        # =================================================

        terminal_statuses = (
            "VERIFIED",
            "BLOCKED",
            "FAILED",
        )


        if (
            decision == "VERIFIED"
            and previous_status
            not in terminal_statuses
        ):

            DEPLOYMENT_SUCCESS.inc()


        elif (
            decision == "BLOCKED"
            and previous_status
            not in terminal_statuses
        ):

            DEPLOYMENT_FAILURE.inc()


        # =================================================
        # Save Prediction Record
        # =================================================

        prediction_record = (
            VerificationService._save_prediction(
                db=db,
                deployment_id=deployment_id,
                prediction_result=prediction_result,
            )
        )


        # =================================================
        # Publish Dashboard Metrics
        # =================================================

        VerificationService._publish_dashboard_metrics(
            deployment=deployment,
            prediction_result=prediction_result,
            deployment_regressions=deployment_regressions,
        )


        # =================================================
        # Return Complete Verification Result
        # =================================================

        return {

            "success": True,

            "deployment_id":
                deployment.id,

            "deployment_name":
                deployment.deployment_name,

            "version":
                deployment.version,

            "environment":
                deployment.environment,

            "verification":
                decision,

            "deployment_status":
                deployment.status,


            # ---------------------------------------------
            # Telemetry
            # ---------------------------------------------

            "telemetry": {

                "cpu_usage":
                    telemetry.cpu_usage,

                "memory_usage":
                    telemetry.memory_usage,

                "latency":
                    telemetry.latency,

                "build_duration":
                    telemetry.build_duration,

                "deployment_duration":
                    telemetry.deployment_duration,

                "error_count":
                    telemetry.error_count,
            },


            # ---------------------------------------------
            # ML Prediction
            # ---------------------------------------------

            "ml_prediction":
                prediction_result,


            "prediction_record_id":
                prediction_record.id,


            # ---------------------------------------------
            # Regression Information
            # ---------------------------------------------

            "regressions":
                deployment_regressions,

            "regression_count":
                len(
                    deployment_regressions
                ),


            # ---------------------------------------------
            # Blocking Reasons
            # ---------------------------------------------

            "blocked_reasons":
                blocked_reasons,


            # ---------------------------------------------
            # AI Analysis
            # ---------------------------------------------

            "ai_analysis": {

                "available":
                    bool(
                        ai_explanation
                    ),

                "explanation":
                    ai_explanation,
            }
        }