from __future__ import annotations

import json

from pathlib import Path

from slmforge.task import detect

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures" / "task_detection"


def load_regression_samples() -> list[dict[str, object]]:
    """Load all regression samples from fixture files."""
    samples = []

    for fixture_file in sorted(FIXTURE_DIR.glob("*.json")):
        with fixture_file.open("r", encoding="utf-8") as f:
            samples.extend(json.load(f))

    return samples


def test_task_detector_regression():
    """
    Regression suite for task detector.

    Ensures detector accuracy stays above 85% across
    representative labelled datasets.
    """

    samples = load_regression_samples()

    assert len(samples) >= 30 , (f"Expected at least 30 regression samples, found {len(samples)}")

    correct = 0
    failures = []

    for idx, sample in enumerate(samples):
        expected = sample["label"]

        result = detect(sample["dataset"])

        if result.task_type == expected:
            correct += 1
        else:
            failures.append(
                (
                    idx,
                    expected,
                    result.task_type,
                    round(result.confidence, 3),
                )
            )

    accuracy = correct / len(samples)

    assert accuracy >= 0.85, (
        f"Regression accuracy {accuracy:.2%} is below the required 85%. "
        f"Correct={correct}/{len(samples)}. "
        f"Failures={failures}"
    )
