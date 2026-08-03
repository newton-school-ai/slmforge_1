"""Per-task metric selector for SLM evaluation.

Maps task types to evaluation metric suites.  Each metric function has the
same call signature so the eval engine can iterate over any suite uniformly.

Task-to-metric mapping
-----------------------
classification -> accuracy, precision, recall, f1
summarisation  -> rouge1, rouge2, rougeL, bleu
qa             -> exact_match, f1_score, bleu
instruction    -> rougeL, bleu
chat           -> rougeL, bleu

Metric call shape
------------------
    fn(predictions: list[str], references: list[str]) -> dict[str, float]

Plug-in interface
------------------
Use the ``\u0040register_metric`` decorator to add new metrics::

    from slmforge.task.metrics import register_metric

    @register_metric(task_types=["classification"])
    def my_metric(predictions, references):
        ...

Or call it imperatively::

    register_metric(task_types=["qa"])(my_metric)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

_METRICS: dict[str, "Metric"] = {}
_TASK_METRICS: dict[str, list[str]] = {}


@dataclass(frozen=True)
class Metric:
    """A registered evaluation metric.

    Attributes:
        name: Unique metric name (e.g. ``"accuracy"``).
        fn: Callable with signature ``(preds, refs) -> dict[str, float]``.
        task_types: Task types this metric applies to.
        description: Human-readable description.
    """

    name: str
    fn: Callable[[list[str], list[str]], dict[str, float]]
    task_types: tuple[str, ...]
    description: str = ""


def register_metric(
    task_types: list[str] | None = None,
    description: str = "",
) -> Callable:
    """Decorator to register a metric function with the global registry.

    The decorated function's name (with any leading ``_`` stripped) is used as
    the metric name.

    Usage::

        @register_metric(task_types=["classification"])
        def accuracy(predictions, references):
            ...
    """

    def decorator(fn: Callable) -> Callable:
        name = fn.__name__.lstrip("_")
        metric = Metric(
            name=name,
            fn=fn,
            task_types=tuple(task_types or []),
            description=description or (fn.__doc__ or "").strip(),
        )
        _METRICS[name] = metric
        for tt in metric.task_types:
            if tt not in _TASK_METRICS:
                _TASK_METRICS[tt] = []
            _TASK_METRICS[tt].append(name)
        return fn

    return decorator


def get_metrics(task_type: str) -> list[Metric]:
    """Return all metrics registered for *task_type*.

    Raises:
        ValueError: If *task_type* is unknown.
    """
    tt = task_type.lower()
    if tt not in _TASK_METRICS:
        raise ValueError(f"Unknown task type: {task_type}")
    return [_METRICS[name] for name in _TASK_METRICS[tt]]


def get_metric(name: str) -> Metric:
    """Look up a single metric by name.

    Raises:
        ValueError: If *name* is not registered.
    """
    if name not in _METRICS:
        raise ValueError(f"Unknown metric: {name}")
    return _METRICS[name]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _check_lengths(predictions: list[str], references: list[str]) -> None:
    if len(predictions) != len(references):
        raise ValueError(
            f"predictions and references must have the same length, "
            f"got {len(predictions)} vs {len(references)}"
        )


# ---------------------------------------------------------------------------
# Default metric implementations
# ---------------------------------------------------------------------------


@register_metric(task_types=["classification"])
def accuracy(predictions: list[str], references: list[str]) -> dict[str, float]:
    from sklearn.metrics import accuracy_score

    _check_lengths(predictions, references)
    if not predictions:
        return {"accuracy": 0.0}
    return {"accuracy": float(accuracy_score(references, predictions))}


@register_metric(task_types=["classification"])
def precision(predictions: list[str], references: list[str]) -> dict[str, float]:
    from sklearn.metrics import precision_score

    _check_lengths(predictions, references)
    if not predictions:
        return {"precision": 0.0}
    return {
        "precision": float(
            precision_score(references, predictions, average="weighted", zero_division=0.0)
        )
    }


@register_metric(task_types=["classification"])
def recall(predictions: list[str], references: list[str]) -> dict[str, float]:
    from sklearn.metrics import recall_score

    _check_lengths(predictions, references)
    if not predictions:
        return {"recall": 0.0}
    return {
        "recall": float(
            recall_score(references, predictions, average="weighted", zero_division=0.0)
        )
    }


@register_metric(task_types=["classification"])
def f1(predictions: list[str], references: list[str]) -> dict[str, float]:
    from sklearn.metrics import f1_score

    _check_lengths(predictions, references)
    if not predictions:
        return {"f1": 0.0}
    return {"f1": float(f1_score(references, predictions, average="weighted", zero_division=0.0))}


@register_metric(task_types=["summarisation"])
def rouge1(predictions: list[str], references: list[str]) -> dict[str, float]:
    from rouge_score import rouge_scorer

    _check_lengths(predictions, references)
    if not predictions:
        return {"rouge1": 0.0}
    scorer = rouge_scorer.RougeScorer(["rouge1"], use_stemmer=True)
    scores = [scorer.score(r, p)["rouge1"].fmeasure for p, r in zip(predictions, references)]
    return {"rouge1": sum(scores) / len(scores)}


@register_metric(task_types=["summarisation"])
def rouge2(predictions: list[str], references: list[str]) -> dict[str, float]:
    from rouge_score import rouge_scorer

    _check_lengths(predictions, references)
    if not predictions:
        return {"rouge2": 0.0}
    scorer = rouge_scorer.RougeScorer(["rouge2"], use_stemmer=True)
    scores = [scorer.score(r, p)["rouge2"].fmeasure for p, r in zip(predictions, references)]
    return {"rouge2": sum(scores) / len(scores)}


@register_metric(task_types=["summarisation", "instruction", "chat"])
def rougeL(predictions: list[str], references: list[str]) -> dict[str, float]:
    from rouge_score import rouge_scorer

    _check_lengths(predictions, references)
    if not predictions:
        return {"rougeL": 0.0}
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    scores = [scorer.score(r, p)["rougeL"].fmeasure for p, r in zip(predictions, references)]
    return {"rougeL": sum(scores) / len(scores)}


@register_metric(task_types=["summarisation", "qa", "instruction", "chat"])
def bleu(predictions: list[str], references: list[str]) -> dict[str, float]:
    from sacrebleu import corpus_bleu

    _check_lengths(predictions, references)
    if not predictions:
        return {"bleu": 0.0}
    result = corpus_bleu(predictions, [references])
    return {"bleu": result.score}


@register_metric(task_types=["qa"])
def exact_match(predictions: list[str], references: list[str]) -> dict[str, float]:
    _check_lengths(predictions, references)
    if not predictions:
        return {"exact_match": 0.0}
    matches = sum(1 for p, r in zip(predictions, references) if p.strip() == r.strip())
    return {"exact_match": matches / len(predictions)}


@register_metric(task_types=["qa"])
def f1_score(predictions: list[str], references: list[str]) -> dict[str, float]:
    _check_lengths(predictions, references)
    if not predictions:
        return {"f1_score": 0.0}

    scores: list[float] = []
    for p, r in zip(predictions, references):
        p_tokens = p.split()
        r_tokens = r.split()
        if not r_tokens:
            scores.append(1.0 if not p_tokens else 0.0)
            continue
        if not p_tokens:
            scores.append(0.0)
            continue
        common = set(p_tokens) & set(r_tokens)
        if not common:
            scores.append(0.0)
            continue
        prec = len(common) / len(p_tokens)
        rec = len(common) / len(r_tokens)
        scores.append(2.0 * prec * rec / (prec + rec))

    return {"f1_score": sum(scores) / len(scores)}
