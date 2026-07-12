from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME")
    APP_VERSION = os.getenv("APP_VERSION")
    APP_DESCRIPTION = os.getenv("APP_DESCRIPTION")
    HOST = os.getenv("HOST")
    PORT = int(os.getenv("PORT"))
    ENVIRONMENT = os.getenv("ENVIRONMENT")
    DATABASE_URL = os.getenv("DATABASE_URL")
    LOG_LEVEL = os.getenv("LOG_LEVEL")
settings = Settings()