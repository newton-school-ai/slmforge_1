from fastapi.testclient import TestClient

from slmforge.api.main import app

client = TestClient(app)


def test_list_builds():
    response = client.get("/builds/")
    assert response.status_code == 200


def test_get_build():
    response = client.get("/builds/test-build")

    assert response.status_code == 200
    assert response.json()["build_id"] == "test-build"


def test_create_build():
    payload = {
        "sources": [
            {
                "type": "public",
                "id": "cnn_dailymail",
            }
        ],
        "task_type": "summarisation",
        "base_model": "auto",
        "lora": {
            "r": 16,
            "alpha": 32,
            "dropout": 0.05,
        },
        "training": {
            "epochs": 2,
            "batch_size": 16,
            "lr": 0.0002,
        },
        "eval": {
            "llm_judge": False,
        },
    }

    response = client.post("/builds/", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "queued"


def test_create_build_invalid_payload():
    response = client.post("/builds/", json={})

    assert response.status_code == 422