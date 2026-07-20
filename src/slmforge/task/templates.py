"""Per-task chat template rendering helpers for instruction-tuned formats."""

from __future__ import annotations

from typing import Any

_SUPPORTED_FORMATS = {"phi3", "llama3.1"}


def _select_first_value(record: dict[str, Any], keys: tuple[str, ...]) -> Any:
    """Return the first value whose key is present and not None."""
    for key in keys:
        if key in record and record[key] is not None:
            return record[key]
    return ""


def apply_chat_template(prompt: str, target: str, format_style: str = "phi3") -> str:
    """Wrap a prompt/target pair in the model-specific chat template markup."""
    if format_style == "phi3":
        return f"<|user|>\n{prompt}<|end|>\n<|assistant|>\n{target}<|end|>"
    if format_style == "llama3.1":
        return (
            f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{prompt}"
            f"<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n{target}<|eot_id|>"
        )
    raise ValueError(f"Unsupported format style: {format_style}")


def render_record(
    record: dict[str, Any],
    task_type: str,
    format_style: str = "phi3",
) -> tuple[str, str]:
    """Render a task record into a structured prompt and target string.

    The helper accepts a record dictionary and extracts the relevant prompt/target values
    based on the task type. The returned values are suitable for use with the matching
    chat template formatters.
    """
    if format_style not in _SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format style: {format_style}")

    task_type = task_type.lower()
    if task_type == "classification":
        input_text = str(_select_first_value(record, ("text", "input", "prompt")))
        target = str(_select_first_value(record, ("label", "target", "output")))
        prompt = f"{input_text}\nLabel:"
        return prompt, target

    if task_type == "summarisation":
        input_text = str(_select_first_value(record, ("document", "text", "input")))
        target = str(_select_first_value(record, ("summary", "target", "output")))
        prompt = f"Summarize:\n{input_text}\nSummary:"
        return prompt, target

    if task_type == "qa":
        question = str(_select_first_value(record, ("question", "prompt", "input")))
        target = str(_select_first_value(record, ("answer", "target", "output")))
        context_value = record.get("context")
        if context_value:
            prompt = f"Context: {context_value}\nQ: {question}\nA:"
        else:
            prompt = f"Q: {question}\nA:"
        return prompt, target

    if task_type == "instruction":
        instruction = str(_select_first_value(record, ("instruction", "prompt")))
        input_value = str(_select_first_value(record, ("input", "context")))
        target = str(_select_first_value(record, ("output", "target", "answer")))
        if input_value:
            prompt = f"{instruction}\n{input_value}\nResponse:"
        else:
            prompt = f"{instruction}\nResponse:"
        return prompt, target

    if task_type == "chat":
        messages = record.get("messages") or []
        if isinstance(messages, list):
            turns = []
            for message in messages:
                if not isinstance(message, dict):
                    continue
                role = str(message.get("role") or message.get("from") or "")
                content = str(message.get("content") or message.get("value") or "")
                if role and content:
                    turns.append(f"{role}: {content}")
            prompt = "\n".join(turns)
        else:
            prompt = ""
        target = ""
        if messages:
            for message in reversed(messages):
                if not isinstance(message, dict):
                    continue
                role = str(message.get("role") or message.get("from") or "")
                content = str(message.get("content") or message.get("value") or "")
                if role.lower() == "assistant" and content:
                    target = content
                    break
        return prompt, target

    raise ValueError(f"Unsupported task type: {task_type}")


def _extract_template_parts(templated_text: str, format_style: str) -> tuple[str, str]:
    """Parse the prompt and target from a rendered template string."""
    if format_style == "phi3":
        prefix = "<|user|>\n"
        suffix = "<|end|>\n<|assistant|>\n"
        end_marker = "<|end|>"
    else:
        prefix = "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n"
        suffix = "<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        end_marker = "<|eot_id|>"

    if not templated_text.startswith(prefix):
        raise ValueError("Template prefix not found")
    if suffix not in templated_text:
        raise ValueError("Template separator not found")
    if not templated_text.endswith(end_marker):
        raise ValueError("Template suffix not found")

    prompt, remainder = templated_text[len(prefix) :].split(suffix, 1)
    target = remainder[: -len(end_marker)]
    return prompt, target


def strip_template(
    templated_text: str,
    task_type: str,
    format_style: str = "phi3",
) -> tuple[str, str]:
    """Extract the original prompt and target from a rendered template string."""
    if format_style not in _SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format style: {format_style}")

    task_type = task_type.lower()
    if task_type in {"classification", "summarisation", "qa", "instruction", "chat"}:
        return _extract_template_parts(templated_text, format_style)

    raise ValueError(f"Unsupported task type: {task_type}")
