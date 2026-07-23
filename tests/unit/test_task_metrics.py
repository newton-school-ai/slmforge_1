"""Tests for the per-task metric selector."""

from __future__ import annotations

import math

import pytest

from slmforge.task.metrics import get_metric, get_metrics, register_metric

_TASK_TYPES = ["classification", "summarisation", "qa", "instruction", "chat"]


def test_each_task_has_non_empty_suite() -> None:
    for tt in _TASK_TYPES:
        metrics = get_metrics(tt)
        assert len(metrics) >= 1, f"{tt} has no metrics"


def test_metric_call_shape() -> None:
    for tt in _TASK_TYPES:
        for metric in get_metrics(tt):
            result = metric.fn(["a"], ["a"])
            assert isinstance(result, dict)
            assert metric.name in result
            assert isinstance(result[metric.name], float)


def test_accuracy() -> None:
    preds = ["a", "b", "c"]
    refs = ["a", "b", "b"]
    result = get_metric("accuracy").fn(preds, refs)
    assert math.isclose(result["accuracy"], 2 / 3)


def test_precision() -> None:
    preds = ["a", "b", "c"]
    refs = ["a", "b", "b"]
    result = get_metric("precision").fn(preds, refs)
    assert 0.0 <= result["precision"] <= 1.0


def test_recall() -> None:
    preds = ["a", "b", "c"]
    refs = ["a", "b", "b"]
    result = get_metric("recall").fn(preds, refs)
    assert 0.0 <= result["recall"] <= 1.0


def test_f1_classification() -> None:
    preds = ["a", "b", "b"]
    refs = ["a", "b", "b"]
    result = get_metric("f1").fn(preds, refs)
    assert math.isclose(result["f1"], 1.0)

    preds = ["b", "b", "b"]
    refs = ["a", "b", "b"]
    result = get_metric("f1").fn(preds, refs)
    assert 0.0 <= result["f1"] <= 1.0


def test_exact_match() -> None:
    em = get_metric("exact_match")

    result = em.fn(["hello", "world"], ["hello", "world"])
    assert math.isclose(result["exact_match"], 1.0)

    result = em.fn(["hello", "world"], ["hello", "there"])
    assert math.isclose(result["exact_match"], 0.5)

    result = em.fn(["hello"], ["world"])
    assert math.isclose(result["exact_match"], 0.0)


def test_qa_f1() -> None:
    f1_score = get_metric("f1_score")

    result = f1_score.fn(["the cat"], ["the cat"])
    assert math.isclose(result["f1_score"], 1.0)

    result = f1_score.fn(["the cat"], ["the dog"])
    assert 0.0 < result["f1_score"] < 1.0

    result = f1_score.fn(["cat"], ["dog"])
    assert math.isclose(result["f1_score"], 0.0)

    result = f1_score.fn(["hello world"], [""])
    assert math.isclose(result["f1_score"], 0.0)


def test_rouge1() -> None:
    r1 = get_metric("rouge1")
    result = r1.fn(["the cat sat on the mat"], ["the cat sat on the mat"])
    assert math.isclose(result["rouge1"], 1.0)


def test_rouge2() -> None:
    r2 = get_metric("rouge2")
    result = r2.fn(["the cat sat on the mat"], ["the cat sat on the mat"])
    assert math.isclose(result["rouge2"], 1.0)


def test_rougeL() -> None:
    rL = get_metric("rougeL")
    result = rL.fn(["the cat sat on the mat"], ["the cat sat on the mat"])
    assert math.isclose(result["rougeL"], 1.0)


def test_bleu() -> None:
    bleu = get_metric("bleu")
    result = bleu.fn(
        ["the cat sat on the mat in the house"],
        ["the cat sat on the mat in the house"],
    )
    assert math.isclose(result["bleu"], 100.0, rel_tol=1e-5)


def test_register_new_metric_plugin() -> None:
    @register_metric(task_types=["classification"], description="My custom metric")
    def my_custom(predictions, references):
        return {"my_custom": 42.0}

    assert "my_custom" in [m.name for m in get_metrics("classification")]
    metric = get_metric("my_custom")
    assert metric.description == "My custom metric"
    assert metric.fn(["x"], ["x"]) == {"my_custom": 42.0}


def test_unknown_task_type() -> None:
    with pytest.raises(ValueError, match="Unknown task type"):
        get_metrics("invalid_type")


def test_unknown_metric_name() -> None:
    with pytest.raises(ValueError, match="Unknown metric"):
        get_metric("nonexistent_metric")


def test_empty_inputs() -> None:
    em = get_metric("exact_match")
    assert em.fn([], []) == {"exact_match": 0.0}

    acc = get_metric("accuracy")
    assert acc.fn([], []) == {"accuracy": 0.0}

    r1 = get_metric("rouge1")
    assert r1.fn([], []) == {"rouge1": 0.0}

    b = get_metric("bleu")
    assert b.fn([], []) == {"bleu": 0.0}


def test_mismatched_lengths() -> None:
    acc = get_metric("accuracy")
    with pytest.raises(ValueError, match="same length"):
        acc.fn(["a", "b"], ["a"])


def test_f1_score_empty_reference() -> None:
    f1_score = get_metric("f1_score")
    result = f1_score.fn([""], [""])
    assert math.isclose(result["f1_score"], 1.0)

    result = f1_score.fn(["hello"], [""])
    assert math.isclose(result["f1_score"], 0.0)


def test_precision_recall_f1_identical() -> None:
    preds = ["a", "b", "c"]
    refs = ["a", "b", "c"]
    for name in ("precision", "recall", "f1"):
        result = get_metric(name).fn(preds, refs)
        assert math.isclose(result[name], 1.0)


def test_classification_all_wrong() -> None:
    preds = ["a", "a", "a"]
    refs = ["b", "b", "b"]
    acc = get_metric("accuracy").fn(preds, refs)
    assert math.isclose(acc["accuracy"], 0.0)
    for name in ("precision", "recall", "f1"):
        result = get_metric(name).fn(preds, refs)
        assert math.isclose(result[name], 0.0), f"{name} should be 0.0"


def test_bleu_no_match() -> None:
    bleu = get_metric("bleu")
    result = bleu.fn(
        ["completely different text here"],
        ["the cat sat on the mat in the house"],
    )
    assert result["bleu"] < 1.0
