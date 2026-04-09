import json
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings

TelemetryMode = Literal["demo", "cluster", "local", "hybrid"]


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://kubewise:kubewise@localhost:5432/kubewise"
    DATABASE_URL_SYNC: str = "postgresql://kubewise:kubewise@localhost:5432/kubewise"
    PROMETHEUS_URL: str = "http://localhost:9090"
    # When MOCK_MODE=false and Prometheus is down/sleeping, still return mock data so the API/UI stay up.
    PROMETHEUS_FALLBACK_MOCK: bool = True
    MOCK_MODE: bool = True
    # When MOCK_MODE=false: cluster=k8s/cAdvisor+kube-state metrics; local=node_exporter; hybrid=cluster then node_exporter; demo=synthetic only.
    TELEMETRY_MODE: TelemetryMode = "cluster"
    # Optional OpenCost UI/API (in-cluster is typical). See https://github.com/opencost/opencost — no public dataset; deploy or leave unset.
    OPENCOST_URL: str = ""
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    ENABLE_METRICS_SCHEDULER: bool = False
    METRICS_COLLECTION_INTERVAL_MINUTES: int = 15
    METRICS_COLLECTION_SCENARIO: str = "wasteful"
    ENABLE_DB_PERSISTENCE: bool = True

    model_config = {"env_file": ".env", "extra": "ignore"}

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("["):
                v = json.loads(s)
            else:
                return [x.strip().rstrip("/") for x in s.split(",") if x.strip()]
        if isinstance(v, list):
            return [str(x).strip().rstrip("/") for x in v if str(x).strip()]
        return v


settings = Settings()


def effective_telemetry_mode() -> TelemetryMode:
    """MOCK_MODE=true forces demo (legacy); otherwise TELEMETRY_MODE is used."""
    if settings.MOCK_MODE:
        return "demo"
    return settings.TELEMETRY_MODE
