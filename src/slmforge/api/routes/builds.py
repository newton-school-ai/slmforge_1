from __future__ import annotations

from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from slmforge.api.schemas import BuildRequest, BuildResponse

router = APIRouter(prefix="/builds", tags=["builds"])


@router.post("", response_model=BuildResponse)
def create_build(payload: BuildRequest) -> BuildResponse:
    """Create a new model fine-tuning build."""
    return BuildResponse(build_id="build_test_001", status="queued")


@router.get("", response_model=List[BuildResponse])
def list_builds() -> List[BuildResponse]:
    """List all model builds."""
    return [BuildResponse(build_id="build_test_001", status="queued")]


@router.get("/{build_id}", response_model=BuildResponse)
def get_build(build_id: str) -> BuildResponse:
    """Get the details/status of a specific build."""
    return BuildResponse(build_id=build_id, status="running")


@router.websocket("/{build_id}/stream")
async def stream_build(websocket: WebSocket, build_id: str) -> None:
    """Stream live build progress events via WebSocket."""
    await websocket.accept()
    try:
        events = [
            {"event": "discover_sources"},
            {"event": "detect_task", "task_type": "summarisation"},
            {"event": "plan", "vram_gb": 18, "est_minutes": 24},
            {"event": "epoch", "epoch": 1, "train_loss": 1.23},
            {"event": "checkpoint", "path": f"builds/{build_id}/checkpoint-epoch-1"},
            {"event": "eval", "metrics": {"rouge_l": 0.62}},
            {"event": "complete", "build_id": build_id},
        ]
        for event in events:
            await websocket.send_json(event)
    except WebSocketDisconnect:
        pass
