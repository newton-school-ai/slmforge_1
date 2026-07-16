from __future__ import annotations

import datasets
import pandas as pd

from slmforge.task import Detection, detect


def test_classification_detection() -> None:
    # 1. Classification dataset: small fixed set of labels (cardinality 2), short labels
    records = [
        {
            "text": f"This is movie review text number {i} which is long and expressive.",
            "label": "positive" if i % 2 == 0 else "negative",
        }
        for i in range(100)
    ]

    # Test with list of dicts
    result = detect(records)
    assert result.task_type == "classification"
    assert result.confidence > 0.4

    # Test with Pandas DataFrame
    df = pd.DataFrame(records)
    result_df = detect(df)
    assert result_df.task_type == "classification"
    assert result_df.confidence == result.confidence

    # Test with HF Dataset
    hf_ds = datasets.Dataset.from_list(records)
    result_hf = detect(hf_ds)
    assert result_hf.task_type == "classification"
    assert result_hf.confidence == result.confidence


def test_summarisation_detection() -> None:
    # 2. Summarisation dataset: input is long, output is much shorter, vocabulary overlap is high
    records = []
    for i in range(50):
        input_text = (
            f"The quick brown fox jumps over the lazy dog. This is sample text number {i}. "
            "We are writing a long document that details the events of a fox jumping over a dog. "
        ) * 5
        target_text = f"Fox jumps over dog in sample {i}."
        records.append({"document": input_text, "summary": target_text})

    result = detect(records)
    assert result.task_type == "summarisation"
    assert result.confidence > 0.4


def test_qa_detection() -> None:
    # 3. QA dataset: presence of question/answer fields, question containing '?', short answers
    records = [
        {
            "question": f"What is the value of parameter {i}?",
            "answer": f"Parameter {i} is set to value {i * 2}.",
            "context": (
                f"This is context block. Parameter {i} is set to value {i * 2} "
                f"and parameter {i + 1} is set."
            ),
        }
        for i in range(50)
    ]

    result = detect(records)
    assert result.task_type == "qa"
    assert result.confidence > 0.4


def test_instruction_detection() -> None:
    # 4. Instruction dataset: presence of instruction/output field, high cardinality (uniqueness)
    records = [
        {
            "instruction": f"Generate a unique list of {i} elements.",
            "input": f"Input info {i}.",
            "output": f"1. Item {i}\n2. Item {i + 1}\n3. Item {i + 2}",
        }
        for i in range(50)
    ]

    result = detect(records)
    assert result.task_type == "instruction"
    assert result.confidence > 0.4


def test_chat_detection() -> None:
    # 5. Chat dataset: role-tagged messages, user/assistant turns
    records = [
        {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Hello, tell me about {i}."},
                {"role": "assistant", "content": f"Hello! {i} is a number."},
            ]
        }
        for i in range(50)
    ]

    result = detect(records)
    assert result.task_type == "chat"
    assert result.confidence > 0.5


def test_defensive_handling_malformed_datasets() -> None:
    # Empty dataset
    result_empty = detect([])
    assert result_empty.task_type == "instruction"
    assert result_empty.confidence == 0.0

    # None input
    result_none = detect(None)
    assert result_none.task_type == "instruction"
    assert result_none.confidence == 0.0

    # Non-standard data formats/types (like an integer or raw string)
    result_invalid_type = detect(123)
    assert result_invalid_type.task_type == "instruction"
    assert result_invalid_type.confidence == 0.0

    # Mixed/partially empty/null fields
    records = [
        {"col1": None, "col2": 123},
        {"col1": "some text", "col2": None},
        {"col1": "other text", "col2": [1, 2, 3]},  # unhashable list
    ]
    result_mixed = detect(records)
    assert isinstance(result_mixed, Detection)
    assert 0.0 <= result_mixed.confidence <= 1.0


def test_low_confidence_threshold() -> None:
    # A dataset that looks ambiguous (e.g. classification vs qa)
    # We mix equal numbers of classification-like and qa-like rows, or structure columns ambiguously
    records = [
        {"query": f"Is this a question {i}?", "response": "yes" if i % 2 == 0 else "no"}
        for i in range(50)
    ]
    result = detect(records)
    # Since it has binary labels ("yes"/"no") but also contains questions,
    # both classification and qa might score.
    # Let's verify confidence is calculated and is a valid float
    assert 0.0 <= result.confidence <= 1.0
    assert result.task_type in {"classification", "qa", "instruction"}


def test_hf_dataset_dict() -> None:
    records = [{"text": f"This is review {i}", "label": str(i % 3)} for i in range(50)]
    ds = datasets.Dataset.from_list(records)
    ds_dict = datasets.DatasetDict({"train": ds})

    result = detect(ds_dict)
    assert result.task_type == "classification"
