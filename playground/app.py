import logging

from fastapi import FastAPI

from playground.routers import evaluation_router, upload_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="LLM Correctness Evaluation PoC",
        description="A FastAPI-based RESTful API service for evaluating LLM model correctness.",
        version="0.1.0",
    )

    app.include_router(upload_router)
    app.include_router(evaluation_router)

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy"}

    return app


app = create_app()
