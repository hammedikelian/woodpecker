import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_bdd_url: str = os.getenv("SERVICE_BDD_URL", "http://localhost:5002")
    vosk_model_path: str = os.getenv("VOSK_MODEL_PATH", "vosk-model-small-fr-0.22")
    fuzzy_threshold: int = int(os.getenv("FUZZY_THRESHOLD", "70"))

    class Config:
        env_file = ".env"


settings = Settings()
