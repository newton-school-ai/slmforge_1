from fastapi import FastAPI
from pydantic import BaseModel

from slmforge.api.routes.builds import router as builds_router

app = FastAPI(
    title="SLMForge API",
    version="0.0.1",
)

app.include_router(builds_router)


class HealthResponse(BaseModel):
    status: str


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")
