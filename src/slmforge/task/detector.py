"""Task Detector Module for SLMForge.

Supported Task Types:
- classification: Small fixed set of repeated labels, low target cardinality, short label values.
- summarisation: Input text significantly longer than target text, high vocabulary overlap
  between input and target.
- qa: Question-answer structure, questions contain ? or interrogative words, answers are
  generally short.
- instruction: Instruction-response structure, optional input/context field, high cardinality
  of prompts and outputs.
- chat: Multi-turn, role-tagged messages in a list structure containing role/content fields.

Heuristic Signals:
- Classification: Checks for columns matching target names with low cardinality
  (unique value ratio < 0.15 or absolute count <= 20) and short strings/integers.
- Summarisation: Compares pairs of string columns, checking if input is >2.5x longer than
  target and they have high token Jaccard similarity.
- QA: Looks for question and answer columns. Questions are checked for interrogation
  marks/words. Answers are checked to ensure they are short text blocks.
- Instruction: Looks for 'instruction' and 'output' columns with high uniqueness
  (cardinality > 0.70).
- Chat: Validates nested dictionaries in list-based structures containing keys
  'role'/'content' or 'from'/'value' and corresponding role markers.

Confidence Calculation:
- Raw task scores in [0, 1] are normalized to sum to 1.0.
- Confidence is calculated as the separation between the top task score and the
  runner-up task score:
    confidence = top_score - runner_up_score
- Low-confidence detections are flagged using the LOW_CONFIDENCE_THRESHOLD = 0.50.

Limitations:
- Relies on a sampled subset (first 100 rows) for fast, lightweight execution.
- Susceptible to edge-case column names and non-standard languages if interrogative check
  is English-only.

Extension Strategy:
- The module is designed with `heuristic_score`, `classifier_score` (stub), and
  `combined_score` functions to facilitate the easy integration of a lightweight ML model.
"""

from __future__ import annotations

import re

from dataclasses import dataclass
from typing import Any

LOW_CONFIDENCE_THRESHOLD: float = 0.50


@dataclass(slots=True)
class Detection:
    task_type: str
    confidence: float
    alternatives: list[tuple[str, float]]


def _extract_dataset_info(dataset: Any) -> tuple[list[str], list[dict[str, Any]]]:
    """Extracts column names and a sample of records from various dataset-like objects.

    Supports:
      - datasets.Dataset
      - datasets.DatasetDict (resolving 'train' split first)
      - pandas.DataFrame
      - list of dictionaries
      - dict of lists
    """
    if dataset is None:
        return [], []

    # 1. Pandas DataFrame (checked first as it has keys/values attributes)
    if hasattr(dataset, "columns") and hasattr(dataset, "to_dict") and hasattr(dataset, "head"):
        columns = [str(c) for c in dataset.columns]
        sample_size = min(len(dataset), 100)
        if sample_size == 0:
            return columns, []
        try:
            return columns, dataset.head(sample_size).to_dict(orient="records")
        except Exception:
            pass

    # 2. Hugging Face Dataset
    if hasattr(dataset, "column_names") and hasattr(dataset, "select"):
        columns = list(dataset.column_names)
        sample_size = min(len(dataset), 100)
        if sample_size == 0:
            return columns, []
        try:
            sampled_ds = dataset.select(range(sample_size))
            return columns, sampled_ds.to_list()
        except Exception:
            pass

    # 3. DatasetDict
    if hasattr(dataset, "keys") and hasattr(dataset, "values") and not isinstance(dataset, dict):
        for split in ["train", "val", "validation", "test", "eval"]:
            if split in dataset:
                return _extract_dataset_info(dataset[split])
        keys = list(dataset.keys())
        if keys:
            return _extract_dataset_info(dataset[keys[0]])
        return [], []

    # 4. Dictionary of lists
    if isinstance(dataset, dict):
        columns = list(dataset.keys())
        if not columns:
            return [], []
        first_val = dataset[columns[0]]
        if isinstance(first_val, list):
            num_rows = len(first_val)
            records = []
            sample_size = min(num_rows, 100)
            for i in range(sample_size):
                record = {}
                for col in columns:
                    col_list = dataset[col]
                    if isinstance(col_list, list) and len(col_list) > i:
                        record[col] = col_list[i]
                records.append(record)
            return columns, records
        else:
            return columns, [dataset]

    # 5. List/tuple of dicts (standard records format)
    if isinstance(dataset, (list, tuple)):
        if not dataset:
            return [], []
        columns = []
        sample_size = min(len(dataset), 100)
        records = []
        for i in range(sample_size):
            item = dataset[i]
            if isinstance(item, dict):
                records.append(item)
                for k in item.keys():
                    if k not in columns:
                        columns.append(k)
        return columns, records

    # 6. Fallback iterable
    if hasattr(dataset, "__iter__"):
        try:
            records = []
            columns = []
            for i, item in enumerate(dataset):
                if i >= 100:
                    break
                if isinstance(item, dict):
                    records.append(item)
                    for k in item.keys():
                        if k not in columns:
                            columns.append(k)
            return columns, records
        except Exception:
            pass

    return [], []


def _score_classification(columns: list[str], records: list[dict[str, Any]]) -> float:
    """Evaluates classification heuristic scoring."""
    if not records:
        return 0.0

    best_col_score = 0.0
    for col in columns:
        vals = [r[col] for r in records if r.get(col) is not None]
        if not vals:
            continue

        # Classification labels are not dictionaries/lists
        if any(isinstance(v, (dict, list)) for v in vals):
            continue

        try:
            unique_vals = set(vals)
        except TypeError:
            continue

        cardinality = len(unique_vals)
        if cardinality < 2 or cardinality > 20:
            continue

        # Check label values are short
        str_vals = [str(v) for v in vals]
        avg_len = sum(len(s) for s in str_vals) / len(str_vals)
        if avg_len > 40:
            continue

        card_score = 1.0 - (cardinality / len(vals))
        name_lower = col.lower()
        is_target_name = name_lower in {
            "label",
            "target",
            "class",
            "category",
            "sentiment",
            "y",
            "output",
            "response",
        }

        col_score = 0.6 * card_score
        if is_target_name:
            col_score += 0.4
        else:
            col_score += 0.2 * (1.0 - avg_len / 40.0)

        best_col_score = max(best_col_score, col_score)

    # Classification datasets typically have input text alongside labels
    has_text_input = any(
        c.lower() in {"text", "sentence", "document", "input", "body", "passage"} for c in columns
    )
    if has_text_input and best_col_score > 0.0:
        best_col_score += 0.1

    return min(best_col_score, 1.0)


def _score_summarisation(columns: list[str], records: list[dict[str, Any]]) -> float:
    """Evaluates summarisation heuristic scoring."""
    if not records or len(columns) < 2:
        return 0.0

    best_pair_score = 0.0
    for col_in in columns:
        for col_out in columns:
            if col_in == col_out:
                continue

            vals_in = [str(r[col_in]) for r in records if r.get(col_in) is not None]
            vals_out = [str(r[col_out]) for r in records if r.get(col_out) is not None]
            if len(vals_in) < 2 or len(vals_out) < 2:
                continue

            avg_len_in = sum(len(s) for s in vals_in) / len(vals_in)
            avg_len_out = sum(len(s) for s in vals_out) / len(vals_out)

            # Summarisation targets should be short, but inputs must be much longer
            if avg_len_out < 10 or avg_len_in < 30:
                continue
            if avg_len_in <= 2.5 * avg_len_out:
                continue

            # Check vocabulary overlap
            overlaps = []
            for r in records:
                val_in = r.get(col_in)
                val_out = r.get(col_out)
                if (
                    not val_in
                    or not val_out
                    or not isinstance(val_in, str)
                    or not isinstance(val_out, str)
                ):
                    continue
                words_in = set(re.findall(r"\b\w+\b", val_in.lower()))
                words_out = set(re.findall(r"\b\w+\b", val_out.lower()))
                if not words_out:
                    continue
                overlap = len(words_in & words_out) / len(words_out)
                overlaps.append(overlap)

            if not overlaps:
                continue
            avg_overlap = sum(overlaps) / len(overlaps)
            if avg_overlap < 0.25:
                continue

            # Length ratio score
            ratio = avg_len_in / avg_len_out
            ratio_score = min(ratio / 10.0, 1.0)
            overlap_score = min(avg_overlap / 0.8, 1.0)

            in_name_match = any(
                k in col_in.lower()
                for k in ["text", "document", "article", "context", "input", "dialogue"]
            )
            out_name_match = any(
                k in col_out.lower() for k in ["summary", "abstract", "title", "output", "target"]
            )

            pair_score = 0.4 * ratio_score + 0.4 * overlap_score
            if in_name_match:
                pair_score += 0.1
            if out_name_match:
                pair_score += 0.1

            best_pair_score = max(best_pair_score, pair_score)

    return min(best_pair_score, 1.0)


def _score_qa(columns: list[str], records: list[dict[str, Any]]) -> float:
    """Evaluates question-answering heuristic scoring."""
    if not records or len(columns) < 2:
        return 0.0

    interrogative_words = {
        "what",
        "how",
        "why",
        "who",
        "where",
        "when",
        "which",
        "can",
        "is",
        "are",
        "do",
        "does",
        "did",
    }
    best_qa_score = 0.0

    for col_q in columns:
        for col_a in columns:
            if col_q == col_a:
                continue

            vals_q = [str(r[col_q]) for r in records if r.get(col_q) is not None]
            vals_a = [str(r[col_a]) for r in records if r.get(col_a) is not None]
            if len(vals_q) < 2 or len(vals_a) < 2:
                continue

            # Check if source strings look like questions
            q_count = 0
            for s in vals_q:
                s_clean = s.strip().lower()
                if s_clean.endswith("?"):
                    q_count += 1
                else:
                    words = s_clean.split()
                    first_word = words[0] if words else ""
                    first_word = "".join(c for c in first_word if c.isalnum())
                    if first_word in interrogative_words:
                        q_count += 1

            q_ratio = q_count / len(vals_q)

            # If it doesn't look like questions and column names are generic, skip
            if q_ratio < 0.25 and not any(k in col_q.lower() for k in ["question", "query", "q"]):
                continue

            try:
                card_a = len(set(vals_a))
            except TypeError:
                continue
            card_ratio_a = card_a / len(vals_a)

            # Answers are generally unique and short
            avg_len_a = sum(len(s) for s in vals_a) / len(vals_a)
            if avg_len_a > 400 or card_ratio_a < 0.5:
                continue

            q_name_match = any(k in col_q.lower() for k in ["question", "query", "q"])
            a_name_match = any(k in col_a.lower() for k in ["answer", "a"])

            score = 0.4 * q_ratio + 0.3 * (1.0 - avg_len_a / 400.0)
            if q_name_match:
                score += 0.15
            if a_name_match:
                score += 0.15

            # Boost if a context column exists
            has_context = any(
                "context" in c.lower() or "passage" in c.lower() or "paragraph" in c.lower()
                for c in columns
            )
            if has_context:
                score += 0.1

            best_qa_score = max(best_qa_score, score)

    return min(best_qa_score, 1.0)


def _score_instruction(columns: list[str], records: list[dict[str, Any]]) -> float:
    """Evaluates instruction/response heuristic scoring."""
    if not records:
        return 0.0

    # Checks for direct instruction/prompt output/response column naming
    has_instruction = any(c.lower() in {"instruction", "prompt", "prompt_text"} for c in columns)
    has_output = any(c.lower() in {"output", "response", "target", "completion"} for c in columns)
    has_input = any(c.lower() in {"input", "context"} for c in columns)

    if has_instruction and has_output:
        inst_cols = [c for c in columns if c.lower() in {"instruction", "prompt", "prompt_text"}]
        out_cols = [
            c for c in columns if c.lower() in {"output", "response", "target", "completion"}
        ]

        vals_inst = [str(r[inst_cols[0]]) for r in records if r.get(inst_cols[0]) is not None]
        vals_out = [str(r[out_cols[0]]) for r in records if r.get(out_cols[0]) is not None]

        if len(vals_inst) >= 2 and len(vals_out) >= 2:
            try:
                unique_inst = len(set(vals_inst))
                unique_out = len(set(vals_out))
            except TypeError:
                return 0.0

            # Instruction-following tasks typically have high-cardinality values
            if unique_inst / len(vals_inst) > 0.7 and unique_out / len(vals_out) > 0.7:
                score = 0.95
                if has_input:
                    score = 1.0
                return score

    # Fallback structure checking for general instruction tasks
    best_inst_score = 0.0
    for col_in in columns:
        for col_out in columns:
            if col_in == col_out:
                continue

            vals_in = [str(r[col_in]) for r in records if r.get(col_in) is not None]
            vals_out = [str(r[col_out]) for r in records if r.get(col_out) is not None]
            if len(vals_in) < 2 or len(vals_out) < 2:
                continue

            try:
                card_in = len(set(vals_in)) / len(vals_in)
                card_out = len(set(vals_out)) / len(vals_out)
            except TypeError:
                continue

            avg_len_in = sum(len(s) for s in vals_in) / len(vals_in)
            avg_len_out = sum(len(s) for s in vals_out) / len(vals_out)

            if card_in > 0.7 and card_out > 0.7 and avg_len_in > 10 and avg_len_out > 10:
                score = 0.4
                if col_in.lower() in {"input", "prompt", "instruction"} or col_out.lower() in {
                    "output",
                    "response",
                    "completion",
                }:
                    score += 0.3
                best_inst_score = max(best_inst_score, score)

    return min(best_inst_score, 1.0)


def _score_chat(columns: list[str], records: list[dict[str, Any]]) -> float:
    """Evaluates chat heuristic scoring."""
    if not records:
        return 0.0

    best_chat_score = 0.0
    for col in columns:
        vals = [r[col] for r in records if r.get(col) is not None]
        if not vals:
            continue

        chat_format_count = 0
        for v in vals:
            if isinstance(v, list) and len(v) > 0:
                valid_turns = 0
                for turn in v:
                    if isinstance(turn, dict):
                        if "role" in turn and "content" in turn:
                            valid_turns += 1
                        elif "from" in turn and "value" in turn:
                            valid_turns += 1
                if valid_turns == len(v):
                    chat_format_count += 1

        chat_ratio = chat_format_count / len(vals)
        if chat_ratio > 0.5:
            score = 0.8 + 0.2 * chat_ratio
            if col.lower() in {"messages", "conversations", "turns", "dialogue"}:
                score += 0.1
            best_chat_score = max(best_chat_score, score)

    return min(best_chat_score, 1.0)


def heuristic_score(dataset: Any) -> dict[str, float]:
    """Computes heuristic scores in [0, 1] for all task types."""
    columns, records = _extract_dataset_info(dataset)
    if not columns or not records:
        return {
            "classification": 0.0,
            "summarisation": 0.0,
            "qa": 0.0,
            "instruction": 0.0,
            "chat": 0.0,
        }

    return {
        "classification": _score_classification(columns, records),
        "summarisation": _score_summarisation(columns, records),
        "qa": _score_qa(columns, records),
        "instruction": _score_instruction(columns, records),
        "chat": _score_chat(columns, records),
    }


def classifier_score(dataset: Any) -> dict[str, float]:
    """Stub for future lightweight classifier scoring."""
    return {
        "classification": 0.0,
        "summarisation": 0.0,
        "qa": 0.0,
        "instruction": 0.0,
        "chat": 0.0,
    }


def combined_score(dataset: Any) -> dict[str, float]:
    """Combines heuristic and classifier scores for task prediction."""
    h_scores = heuristic_score(dataset)
    c_scores = classifier_score(dataset)

    # If classifier is completely empty/stub, use purely heuristic scores
    if all(v == 0.0 for v in c_scores.values()):
        return h_scores

    alpha = 0.7  # Heuristic weight
    return {
        task: alpha * h_scores[task] + (1 - alpha) * c_scores.get(task, 0.0) for task in h_scores
    }


def detect(dataset: Any) -> Detection:
    """Analyzes a dataset's schema and contents to detect its training task type.

    Args:
        dataset: The dataset-like object (Hugging Face Dataset, DatasetDict,
          Pandas DataFrame, dict, or list of dicts).

    Returns:
        Detection: A Detection object with the top predicted task type, confidence,
        and alternative candidates ranked.
    """
    columns, records = _extract_dataset_info(dataset)

    # Fallback if the dataset is empty, missing, or malformed
    if not columns or not records:
        return Detection(
            task_type="instruction",
            confidence=0.0,
            alternatives=[
                ("classification", 0.0),
                ("summarisation", 0.0),
                ("qa", 0.0),
                ("chat", 0.0),
            ],
        )

    scores = combined_score(dataset)

    # Normalize scores so they sum to 1.0 (L1 normalization)
    total_score = sum(scores.values())
    if total_score <= 0.0:
        normalized_scores = {k: 1.0 / len(scores) for k in scores}
    else:
        normalized_scores = {k: v / total_score for k, v in scores.items()}

    ranked = sorted(normalized_scores.items(), key=lambda item: item[1], reverse=True)

    top_task, top_score = ranked[0]
    runner_up_task, runner_up_score = ranked[1] if len(ranked) > 1 else (None, 0.0)

    # Confidence represents the separation between top and runner-up
    confidence = top_score - runner_up_score

    alternatives = [(task, float(round(score, 4))) for task, score in ranked[1:]]

    return Detection(
        task_type=top_task,
        confidence=float(round(confidence, 4)),
        alternatives=alternatives,
    )
