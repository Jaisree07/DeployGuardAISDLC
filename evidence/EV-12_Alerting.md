# EV-12 – Deployment Monitoring and Automated Alerting

## Deliverable

**D-12 – Prometheus and Grafana alerting for deployment failures, high deployment risk, anomalies, regressions and high latency.**

## Objective

This evidence demonstrates the implementation of automated deployment monitoring and alerting in DeployGuard AI using Prometheus and Grafana.

The alerting framework evaluates deployment health, risk, anomaly, regression and latency metrics and generates alerts when predefined deployment conditions are detected.

## Alert Conditions Implemented

The following deployment alert conditions are configured:

- **DeploymentBlocked** – triggered when deployment failures are detected.
- **HighDeploymentRisk** – triggered when DeployGuard AI identifies high deployment risk.
- **DeploymentAnomaly** – triggered when Isolation Forest detects anomalous deployment behaviour.
- **DeploymentRegression** – triggered when deployment regression is detected.
- **HighDeploymentLatency** – triggered when deployment latency exceeds the configured threshold.

## Evidence 1 – Prometheus Alert Rules

<img width="946" height="461" alt="image" src="https://github.com/user-attachments/assets/10edb149-c87e-43e8-a84d-c6c1d9cbf150" />


The screenshot demonstrates the configured Prometheus alert rules used to evaluate deployment failure, deployment risk, anomaly, regression and latency conditions.

## Evidence 2 – Grafana Alerting Configuration

<img width="796" height="457" alt="image" src="https://github.com/user-attachments/assets/b9047fca-f78f-4819-8540-f0688519c694" />

<img width="819" height="407" alt="image" src="https://github.com/user-attachments/assets/463ad182-a60f-4fa4-a5c0-45139123e8fb" />

The screenshot demonstrates the Grafana alerting configuration used to monitor deployment conditions and trigger operational notifications.

## Verification

The alerting workflow was validated using DeployGuard AI deployment metrics.

Prometheus evaluates the configured alert expressions at regular intervals. When the corresponding deployment condition is satisfied, the alert transitions to the appropriate alert state and can be consumed by Grafana Alerting for operational notification.

The implementation therefore provides automated monitoring rather than relying only on manual dashboard inspection.

## Alerting Flow

**Deployment Telemetry → Prometheus Metrics → Alert Rule Evaluation → Alert State → Grafana Alerting → Operational Notification**

## Source Implementation

The primary alert configuration is maintained in:

`monitoring/prometheus/alert_rules.yml`

The Prometheus configuration references the alert rule file through:

`monitoring/prometheus/prometheus.yml`

Relevant deployment metrics include:

- `deployment_failure_total`
- `deployment_predicted_risk`
- `deployment_anomaly_detected`
- `deployguard_regression_detected`
- `deployment_latency_ms`

## Conclusion

This evidence confirms that DeployGuard AI provides automated deployment monitoring and alerting for deployment failures, high deployment risk, anomalous behaviour, deployment regressions and high latency conditions using Prometheus and Grafana.

**Evidence ID:** EV-12  
**Deliverable ID:** D-12
