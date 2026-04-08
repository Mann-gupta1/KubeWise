import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import cost, health, metrics, recommendations, simulations

logger = logging.getLogger("kubewise")


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = None
    try:
        from app.db.session import engine as db_engine
        from app.db.models import Base

        engine = db_engine
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized")
    except Exception:
        logger.warning("Database unavailable -- running in API-only mock mode")

    from app.scheduler_service import (
        shutdown_metrics_scheduler,
        start_metrics_scheduler,
    )

    start_metrics_scheduler()
    try:
        yield
    finally:
        shutdown_metrics_scheduler()
        if engine is not None:
            try:
                await engine.dispose()
            except Exception:
                pass


app = FastAPI(
    title="KubeWise",
    description="Kubernetes Cost Intelligence & Autoscaling Advisor",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.API_V1_PREFIX)
app.include_router(metrics.router, prefix=settings.API_V1_PREFIX)
app.include_router(recommendations.router, prefix=settings.API_V1_PREFIX)
app.include_router(cost.router, prefix=settings.API_V1_PREFIX)
app.include_router(simulations.router, prefix=settings.API_V1_PREFIX)
