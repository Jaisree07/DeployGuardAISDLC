from locust import HttpUser, task, between
import random


class DeployGuardLoadTest(HttpUser):

    wait_time = between(1, 3)

    def on_start(self):
        self.deployment_id = None

    # ========================================================
    # Health Check
    # ========================================================

    @task(3)
    def health_check(self):
        with self.client.get(
            "/health",
            name="GET /health",
            catch_response=True
        ) as response:

            if response.status_code != 200:
                response.failure(
                    f"Health check failed: {response.status_code}"
                )

    # ========================================================
    # Root Endpoint
    # ========================================================

    @task(2)
    def root_endpoint(self):
        with self.client.get(
            "/",
            name="GET /",
            catch_response=True
        ) as response:

            if response.status_code != 200:
                response.failure(
                    f"Root endpoint failed: {response.status_code}"
                )

    # ========================================================
    # Prometheus Metrics
    # ========================================================

    @task(2)
    def metrics_endpoint(self):
        with self.client.get(
            "/metrics",
            name="GET /metrics",
            catch_response=True
        ) as response:

            if response.status_code != 200:
                response.failure(
                    f"Metrics request failed: {response.status_code}"
                )

    # ========================================================
    # Create Deployment
    # ========================================================

    @task(3)
    def create_deployment(self):

        payload = {
            "deployment_name": (
                f"LoadTest-"
                f"{random.randint(1000, 999999)}"
            ),
            "version": "1.0.0",
            "environment": random.choice(
                ["DEV", "QA", "UAT", "PROD"]
            ),
            "status": "Running"
        }

        with self.client.post(
            "/deployments/",
            json=payload,
            name="POST /deployments/",
            catch_response=True
        ) as response:

            if response.status_code not in [200, 201]:
                response.failure(
                    f"Deployment creation failed: "
                    f"{response.status_code}"
                )
                return

            try:
                data = response.json()

                if "id" not in data:
                    response.failure(
                        "Deployment response does not contain id"
                    )
                    return

                self.deployment_id = data["id"]

            except Exception as exc:
                response.failure(
                    f"Invalid deployment response: {exc}"
                )

    # ========================================================
    # Create Telemetry
    # ========================================================

    @task(3)
    def create_telemetry(self):

        if self.deployment_id is None:
            return

        payload = {
            "deployment_id": self.deployment_id,
            "cpu_usage": round(
                random.uniform(20, 95), 2
            ),
            "memory_usage": round(
                random.uniform(20, 95), 2
            ),
            "latency": round(
                random.uniform(50, 900), 2
            ),
            "build_duration": round(
                random.uniform(30, 300), 2
            ),
            "deployment_duration": round(
                random.uniform(20, 180), 2
            ),
            "error_count": random.randint(0, 10)
        }

        with self.client.post(
            "/telemetry/",
            json=payload,
            name="POST /telemetry/",
            catch_response=True
        ) as response:

            if response.status_code not in [200, 201]:
                response.failure(
                    f"Telemetry creation failed: "
                    f"{response.status_code}"
                )

    # ========================================================
    # Prediction
    # ========================================================

    @task(2)
    def prediction(self):

        payload = {
            "environment": random.choice(
                ["DEV", "QA", "UAT", "PROD"]
            ),
            "cpu_usage": round(
                random.uniform(20, 95), 2
            ),
            "memory_usage": round(
                random.uniform(20, 95), 2
            ),
            "latency": round(
                random.uniform(50, 900), 2
            ),
            "build_duration": round(
                random.uniform(30, 300), 2
            ),
            "deployment_duration": round(
                random.uniform(20, 180), 2
            ),
            "error_count": random.randint(0, 10)
        }

        with self.client.post(
            "/predict/",
            json=payload,
            name="POST /predict/",
            catch_response=True
        ) as response:

            if response.status_code not in [200, 201]:
                response.failure(
                    f"Prediction failed: "
                    f"{response.status_code}"
                )

    # ========================================================
    # Verification
    # ========================================================

    @task(1)
    def verification(self):

        if self.deployment_id is None:
            return

        with self.client.post(
            f"/verify/{self.deployment_id}",
            name="POST /verify/{deployment_id}",
            catch_response=True
        ) as response:

            if response.status_code not in [200, 201]:
                response.failure(
                    f"Verification failed: "
                    f"{response.status_code}"
                )
