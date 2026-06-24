from fastapi import APIRouter, WebSocket

from slmforge.api.schemas import BuildRequest, BuildResponse

router = APIRouter(
    prefix="/builds",
    tags=["builds"],
)


@router.post("/", response_model=BuildResponse)
def create_build(build_request: BuildRequest) -> BuildResponse:
    """Create a new build request."""

    _ = build_request

    return BuildResponse(
        build_id="stub-build",
        status="queued",
    )


@router.get("/", response_model=list[BuildResponse])
def list_builds() -> list[BuildResponse]:
    """List all builds."""

    return []


@router.get("/{build_id}", response_model=BuildResponse)
def get_build(build_id: str) -> BuildResponse:
    """Get build details."""

    return BuildResponse(
        build_id=build_id,
        status="queued",
    )


@router.websocket("/{build_id}/stream")
async def stream_build(websocket: WebSocket, build_id: str):
    """Stream build events."""

    await websocket.accept()

    await websocket.send_json(
        {
            "event": "connected",
            "build_id": build_id,
        }
    )

    await websocket.close()
