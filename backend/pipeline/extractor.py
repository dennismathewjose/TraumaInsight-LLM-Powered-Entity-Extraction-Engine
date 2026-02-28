"""LLM extraction via Ollama — send passages + prompt, parse JSON response."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

import requests

from pipeline.config import (
    DEFAULT_LLM_MODEL,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    OLLAMA_BASE_URL,
)
from pipeline.retriever import RetrievedPassage


@dataclass
class ExtractionResult:
    """Result from a single LLM extraction call."""

    value: str
    citation: str
    reasoning: str
    raw_response: str
    model: str
    success: bool
    error: str | None = None


def _format_passages(passages: list[RetrievedPassage]) -> str:
    """Format retrieved passages as a numbered list."""
    parts: list[str] = []
    for i, p in enumerate(passages, 1):
        parts.append(f"[{i}] (Source: {p.note_type}, similarity: {p.similarity_score:.2f})\n{p.text}")
    return "\n\n".join(parts)


def _parse_json_from_response(text: str) -> dict | None:
    """Try to extract a JSON object from the LLM's response text."""
    # Try direct JSON parse first
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Try to find JSON object in the response
    match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Try to find JSON with nested braces
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


def _call_ollama(prompt: str, model: str) -> str:
    """Call Ollama generate endpoint and return the response text."""
    resp = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": model,
            "system": (
                "You are a clinical data extraction assistant. "
                "Always respond with a single valid JSON object and nothing else. "
                "Do not include any text before or after the JSON."
            ),
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": LLM_TEMPERATURE,
                "num_predict": LLM_MAX_TOKENS,
            },
        },
        timeout=300,
    )
    resp.raise_for_status()
    return resp.json().get("response", "")


def extract(
    passages: list[RetrievedPassage],
    field_config: dict,
    model: str = DEFAULT_LLM_MODEL,
) -> ExtractionResult:
    """Run LLM extraction for a single registry field."""
    formatted = _format_passages(passages)
    prompt = field_config["extraction_prompt"].replace("{passages}", formatted)

    try:
        raw = _call_ollama(prompt, model)
    except Exception as e:
        return ExtractionResult(
            value="Extraction failed",
            citation="",
            reasoning="",
            raw_response="",
            model=model,
            success=False,
            error=f"Ollama call failed: {e}",
        )

    parsed = _parse_json_from_response(raw)

    # Retry once if JSON parsing failed
    if parsed is None:
        retry_prompt = prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON. No other text."
        try:
            raw = _call_ollama(retry_prompt, model)
        except Exception as e:
            return ExtractionResult(
                value="Extraction failed",
                citation="",
                reasoning="",
                raw_response=raw,
                model=model,
                success=False,
                error=f"Ollama retry failed: {e}",
            )
        parsed = _parse_json_from_response(raw)

    if parsed is None:
        return ExtractionResult(
            value="Extraction failed",
            citation="",
            reasoning="",
            raw_response=raw,
            model=model,
            success=False,
            error="Failed to parse JSON from LLM response after retry",
        )

    return ExtractionResult(
        value=parsed.get("value", "Unknown"),
        citation=parsed.get("citation", ""),
        reasoning=parsed.get("reasoning", ""),
        raw_response=raw,
        model=model,
        success=True,
    )
