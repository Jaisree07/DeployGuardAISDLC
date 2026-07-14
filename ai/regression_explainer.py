class RegressionExplainer:

    @staticmethod
    def explain(data):

        causes = []
        recommendations = []

        if data["cpu_usage"] > 85:

            causes.append(
                "High CPU utilization detected after deployment."
            )

            recommendations.append(
                "Increase CPU allocation or scale the application horizontally."
            )

        if data["memory_usage"] > 85:

            causes.append(
                "High memory consumption indicates possible memory pressure."
            )

            recommendations.append(
                "Increase memory allocation or investigate memory leaks."
            )

        if data["latency"] > 700:

            causes.append(
                "Application latency increased significantly after deployment."
            )

            recommendations.append(
                "Investigate API bottlenecks and optimize slow database queries."
            )

        if data["build_duration"] > 220:

            causes.append(
                "Build duration exceeded the expected threshold."
            )

            recommendations.append(
                "Optimize the CI pipeline and reduce unnecessary build steps."
            )

        if data["deployment_duration"] > 90:

            causes.append(
                "Deployment rollout took longer than expected."
            )

            recommendations.append(
                "Check deployment scripts and infrastructure resources."
            )

        if data["error_count"] > 2:

            causes.append(
                "Application generated multiple runtime errors after deployment."
            )

            recommendations.append(
                "Review application logs and fix runtime exceptions."
            )

        if not causes:

            causes.append(
                "No significant regression indicators were detected."
            )

            recommendations.append(
                "Deployment is healthy. Continue monitoring production metrics."
            )

        return {

            "root_causes": causes,

            "recommendations": recommendations

        }