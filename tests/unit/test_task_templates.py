from __future__ import annotations

import pytest

from slmforge.task.templates import render_record, strip_template


@pytest.mark.parametrize("format_style", ["phi3", "llama3.1"])
def test_render_and_strip_classification(format_style: str) -> None:
    record = {"text": "This movie was fantastic.", "label": "positive"}

    prompt, target = render_record(record, "classification", format_style=format_style)

    assert prompt == "This movie was fantastic."
    assert target == "positive"
    assert strip_template(_format_text(prompt, target, format_style), "classification", format_style=format_style) == (
        prompt,
        target,
    )


@pytest.mark.parametrize("format_style", ["phi3", "llama3.1"])
def test_render_and_strip_summarisation(format_style: str) -> None:
    record = {"document": "A long article about the moon landing.", "summary": "The moon landing was historic."}

    prompt, target = render_record(record, "summarisation", format_style=format_style)

    assert prompt == "A long article about the moon landing."
    assert target == "The moon landing was historic."
    assert strip_template(_format_text(prompt, target, format_style), "summarisation", format_style=format_style) == (
        prompt,
        target,
    )


@pytest.mark.parametrize("format_style", ["phi3", "llama3.1"])
def test_render_and_strip_qa(format_style: str) -> None:
    record = {"question": "What is the capital of France?", "answer": "Paris"}

    prompt, target = render_record(record, "qa", format_style=format_style)

    assert prompt == "What is the capital of France?"
    assert target == "Paris"
    assert strip_template(_format_text(prompt, target, format_style), "qa", format_style=format_style) == (
        prompt,
        target,
    )


@pytest.mark.parametrize("format_style", ["phi3", "llama3.1"])
def test_render_and_strip_instruction(format_style: str) -> None:
    record = {
        "instruction": "Write a short poem.",
        "input": "About the ocean.",
        "output": "Blue waves whisper at dawn.",
    }

    prompt, target = render_record(record, "instruction", format_style=format_style)

    assert prompt == "Write a short poem.\n\nAbout the ocean."
    assert target == "Blue waves whisper at dawn."
    assert strip_template(_format_text(prompt, target, format_style), "instruction", format_style=format_style) == (
        prompt,
        target,
    )


@pytest.mark.parametrize("format_style", ["phi3", "llama3.1"])
def test_render_and_strip_chat(format_style: str) -> None:
    record = {
        "messages": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
    }

    prompt, target = render_record(record, "chat", format_style=format_style)

    assert prompt == "user: Hello\nassistant: Hi there!"
    assert target == "Hi there!"
    assert strip_template(_format_text(prompt, target, format_style), "chat", format_style=format_style) == (
        prompt,
        target,
    )


def _format_text(prompt: str, target: str, format_style: str) -> str:
    if format_style == "phi3":
        return f"<|user|>\n{prompt}<|end|>\n<|assistant|>\n{target}<|end|>"
    if format_style == "llama3.1":
        return (
            f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{prompt}"
            f"<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n{target}<|eot_id|>"
        )
    raise ValueError(f"Unsupported format style: {format_style}")
