from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from slmforge.api.db import Base


class Build(Base):
    __tablename__ = "builds"

    id = Column(String, primary_key=True, index=True)
    status = Column(String, default="PENDING", nullable=False)
    task_type = Column(String, nullable=False)
    base_model = Column(String, nullable=False)
    lora_config = Column(JSON, nullable=True)
    training_config = Column(JSON, nullable=True)
    eval_config = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    runs = relationship("Run", back_populates="build", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="build", cascade="all, delete-orphan")
    datasets = relationship("Dataset", back_populates="build", cascade="all, delete-orphan")
    evals = relationship("Eval", back_populates="build", cascade="all, delete-orphan")
    serves = relationship("Serve", back_populates="build", cascade="all, delete-orphan")


class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    build_id = Column(String, ForeignKey("builds.id"), nullable=False)
    status = Column(String, nullable=False)
    current_epoch = Column(Integer, default=0, nullable=False)
    train_loss = Column(Float, nullable=True)
    val_loss = Column(Float, nullable=True)
    gpu_util = Column(Float, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)

    # Relationships
    build = relationship("Build", back_populates="runs")


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    build_id = Column(String, ForeignKey("builds.id"), nullable=False)
    type = Column(String, nullable=False)  # local, public, synthetic, internal
    path = Column(String, nullable=True)
    hf_id = Column(String, nullable=True)
    generator = Column(String, nullable=True)
    size = Column(Integer, nullable=True)
    seed = Column(Integer, nullable=True)
    license = Column(String, nullable=True)

    # Relationships
    build = relationship("Build", back_populates="sources")


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    build_id = Column(String, ForeignKey("builds.id"), nullable=False)
    train_size = Column(Integer, nullable=True)
    val_size = Column(Integer, nullable=True)
    eval_size = Column(Integer, nullable=True)
    split_seed = Column(Integer, nullable=True)
    dataset_card_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    build = relationship("Build", back_populates="datasets")


class Eval(Base):
    __tablename__ = "evals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    build_id = Column(String, ForeignKey("builds.id"), nullable=False)
    metrics = Column(JSON, nullable=True)
    llm_judge_verdict = Column(JSON, nullable=True)
    ship_gate_verdict = Column(String, nullable=True)
    report_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    build = relationship("Build", back_populates="evals")


class Serve(Base):
    __tablename__ = "serves"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    build_id = Column(String, ForeignKey("builds.id"), nullable=False)
    status = Column(String, nullable=False)  # RUNNING, STOPPED
    port = Column(Integer, nullable=True)
    host = Column(String, nullable=True)
    auth_enabled = Column(Boolean, default=False, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)

    # Relationships
    build = relationship("Build", back_populates="serves")
