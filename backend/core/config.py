from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME", "DeployGuard AI")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    APP_DESCRIPTION = os.getenv(
        "APP_DESCRIPTION",
        "AI-Powered Deployment Verification & Regression Detection Platform"
    )

    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "8000"))

    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./deployguard.db"
    )

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()