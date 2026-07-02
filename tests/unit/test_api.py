from __future__ import annotations

from fastapi.testclient import TestClient

from slmforge.api.main import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_post_builds_valid() -> None:
    valid_payload = {
        "sources": [
            {"type": "local", "path": "/data/train.jsonl"},
            {"type": "public", "id": "cnn_dailymail"},
            {"type": "synthetic", "generator": "feedback_summariser", "size": 20000, "seed": 42},
        ],
        "task_type": "summarisation",
        "base_model": "auto",
        "lora": {"r": 16, "alpha": 32, "dropout": 0.05},
        "training": {"epochs": 2, "batch_size": 16, "lr": 0.0002},
        "eval": {"llm_judge": False},
    }
    r = client.post("/builds", json=valid_payload)
    assert r.status_code == 200
    data = r.json()
    assert data["build_id"] == "build_test_001"
    assert data["status"] == "queued"


def test_post_builds_invalid_root() -> None:
    # Missing required root fields like task_type
    invalid_payload = {
        "sources": [],
        "base_model": "auto",
        "lora": {"r": 16, "alpha": 32, "dropout": 0.05},
        "training": {"epochs": 2, "batch_size": 16, "lr": 0.0002},
        "eval": {"llm_judge": False},
    }
    r = client.post("/builds", json=invalid_payload)
    assert r.status_code == 422


def test_post_builds_invalid_local_source() -> None:
    # Local source type missing path
    invalid_payload = {
        "sources": [
            {"type": "local"},
        ],
        "task_type": "summarisation",
        "base_model": "auto",
        "lora": {"r": 16, "alpha": 32, "dropout": 0.05},
        "training": {"epochs": 2, "batch_size": 16, "lr": 0.0002},
        "eval": {"llm_judge": False},
    }
    r = client.post("/builds", json=invalid_payload)
    assert r.status_code == 422


def test_post_builds_invalid_public_source() -> None:
    # Public source type missing id
    invalid_payload = {
        "sources": [
            {"type": "public"},
        ],
        "task_type": "summarisation",
        "base_model": "auto",
        "lora": {"r": 16, "alpha": 32, "dropout": 0.05},
        "training": {"epochs": 2, "batch_size": 16, "lr": 0.0002},
        "eval": {"llm_judge": False},
    }
    r = client.post("/builds", json=invalid_payload)
    assert r.status_code == 422


def test_post_builds_invalid_synthetic_source() -> None:
    # Synthetic source type missing generator
    invalid_payload = {
        "sources": [
            {"type": "synthetic", "size": 100},
        ],
        "task_type": "summarisation",
        "base_model": "auto",
        "lora": {"r": 16, "alpha": 32, "dropout": 0.05},
        "training": {"epochs": 2, "batch_size": 16, "lr": 0.0002},
        "eval": {"llm_judge": False},
    }
    r = client.post("/builds", json=invalid_payload)
    assert r.status_code == 422


def test_get_builds() -> None:
    r = client.get("/builds")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["build_id"] == "build_test_001"
    assert data[0]["status"] == "queued"


def test_get_build_by_id() -> None:
    r = client.get("/builds/build_test_999")
    assert r.status_code == 200
    data = r.json()
    assert data["build_id"] == "build_test_999"
    assert data["status"] == "running"


def test_websocket_stream() -> None:
    with client.websocket_connect("/builds/build_test_123/stream") as websocket:
        events = [websocket.receive_json() for _ in range(7)]
        assert events[0]["event"] == "discover_sources"
        assert events[1]["event"] == "detect_task"
        assert events[1]["task_type"] == "summarisation"
        assert events[2]["event"] == "plan"
        assert events[3]["event"] == "epoch"
        assert events[4]["event"] == "checkpoint"
        assert events[5]["event"] == "eval"
        assert events[6]["event"] == "complete"
        assert events[6]["build_id"] == "build_test_123"
