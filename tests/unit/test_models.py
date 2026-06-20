from datetime import datetime
# pyrefly: ignore [missing-import]
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from slmforge.api.db import Base
from slmforge.engine.state import Build, Dataset, Eval, Run, Serve, Source


@pytest.fixture(name="db_session")
def fixture_db_session():
    # Use in-memory SQLite for isolated tests
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_build_model(db_session) -> None:
    build = Build(
        id="build_test_123",
        status="PENDING",
        task_type="summarisation",
        base_model="auto",
        lora_config={"r": 16, "alpha": 32},
        training_config={"epochs": 2},
        eval_config={"llm_judge": False},
    )
    db_session.add(build)
    db_session.commit()

    db_build = db_session.query(Build).filter(Build.id == "build_test_123").first()
    assert db_build is not None
    assert db_build.status == "PENDING"
    assert db_build.task_type == "summarisation"
    assert db_build.lora_config == {"r": 16, "alpha": 32}
    assert db_build.created_at is not None


def test_run_model(db_session) -> None:
    build = Build(id="build_test_123", status="RUNNING", task_type="classification", base_model="auto")
    db_session.add(build)
    db_session.commit()

    run = Run(
        build_id="build_test_123",
        status="RUNNING",
        current_epoch=1,
        train_loss=0.42,
        val_loss=0.45,
        gpu_util=85.5,
    )
    db_session.add(run)
    db_session.commit()

    db_run = db_session.query(Run).filter(Run.build_id == "build_test_123").first()
    assert db_run is not None
    assert db_run.status == "RUNNING"
    assert db_run.current_epoch == 1
    assert db_run.train_loss == 0.42
    assert db_run.gpu_util == 85.5


def test_source_model(db_session) -> None:
    build = Build(id="build_test_123", status="PENDING", task_type="qa", base_model="auto")
    db_session.add(build)
    db_session.commit()

    source = Source(
        build_id="build_test_123",
        type="local",
        path="/data/train.jsonl",
        size=1000,
        seed=42,
        license="MIT",
    )
    db_session.add(source)
    db_session.commit()

    db_source = db_session.query(Source).filter(Source.build_id == "build_test_123").first()
    assert db_source is not None
    assert db_source.type == "local"
    assert db_source.path == "/data/train.jsonl"
    assert db_source.seed == 42


def test_dataset_model(db_session) -> None:
    build = Build(id="build_test_123", status="PENDING", task_type="chat", base_model="auto")
    db_session.add(build)
    db_session.commit()

    dataset = Dataset(
        build_id="build_test_123",
        train_size=800,
        val_size=100,
        eval_size=100,
        split_seed=42,
        dataset_card_path="builds/build_test_123/dataset_card.md",
    )
    db_session.add(dataset)
    db_session.commit()

    db_dataset = db_session.query(Dataset).filter(Dataset.build_id == "build_test_123").first()
    assert db_dataset is not None
    assert db_dataset.train_size == 800
    assert db_dataset.dataset_card_path == "builds/build_test_123/dataset_card.md"


def test_eval_model(db_session) -> None:
    build = Build(id="build_test_123", status="PENDING", task_type="instruction", base_model="auto")
    db_session.add(build)
    db_session.commit()

    eval_result = Eval(
        build_id="build_test_123",
        metrics={"rouge_l": 0.62, "accuracy": 0.91},
        llm_judge_verdict={"win_rate": 0.75},
        ship_gate_verdict="PASS",
        report_path="builds/build_test_123/eval_report.md",
    )
    db_session.add(eval_result)
    db_session.commit()

    db_eval = db_session.query(Eval).filter(Eval.build_id == "build_test_123").first()
    assert db_eval is not None
    assert db_eval.metrics == {"rouge_l": 0.62, "accuracy": 0.91}
    assert db_eval.ship_gate_verdict == "PASS"


def test_serve_model(db_session) -> None:
    build = Build(id="build_test_123", status="PENDING", task_type="instruction", base_model="auto")
    db_session.add(build)
    db_session.commit()

    serve = Serve(
        build_id="build_test_123",
        status="RUNNING",
        port=8000,
        host="localhost",
        auth_enabled=True,
    )
    db_session.add(serve)
    db_session.commit()

    db_serve = db_session.query(Serve).filter(Serve.build_id == "build_test_123").first()
    assert db_serve is not None
    assert db_serve.status == "RUNNING"
    assert db_serve.port == 8000
    assert db_serve.auth_enabled is True
