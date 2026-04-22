from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.api.v1 import auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    print(f"Starting up in {settings.env} mode")
    yield
    print("Shutting down")


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Vacation Planner",
        description="An intelligent assistant that helps users plan trips end-to-end using conversational AI.",
        version="1.0.0",
        lifespan=lifespan,
    )

    @app.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:  # type: ignore
        return {"status": "ok"}

    app.include_router(auth.router)

    return app


app = create_app()
