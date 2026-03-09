from __future__ import annotations

import re
from typing import Any

from detect_ai_score import analyze_text


WORD_RE = re.compile(r"\b[\w'-]+\b")
MULTISPACE_RE = re.compile(r"\s+")
TRIPLET_RE = re.compile(r"\b([^,]{3,40}),\s+([^,]{3,40}),\s+and\s+([^,]{3,40})")


BASE_REPLACEMENTS: list[tuple[str, str]] = [
    ("provides a comprehensive assessment of", "assesses"),
    ("detailed recommendations for improvement", "clear recommendations"),
    ("significant opportunities for enhancement", "clear ways to improve"),
    ("across multiple dimensions", "across the main areas"),
    ("follows a minimalist approach", "uses a minimal approach"),
    ("low barrier to entry", "easy to adopt"),
    ("in order to", "to"),
    ("it is important to note that", ""),
    ("the current implementation", "the current setup"),
    ("user-friendly", "easy to use"),
    ("feature-rich", "useful"),
    ("dramatically improves", "improves"),
]


def _normalize(text: str) -> str:
    return MULTISPACE_RE.sub(" ", text).strip()


def _split_long_sentences(text: str) -> str:
    lines: list[str] = []
    for chunk in text.split("\n"):
        sentence = chunk
        if len(WORD_RE.findall(sentence)) > 28:
            sentence = sentence.replace("; ", ". ")
            sentence = sentence.replace(", which ", ". This ")
            sentence = sentence.replace(", while ", ". At the same time, ")
            sentence = sentence.replace(", and ", ". It also ")
        lines.append(sentence)
    return "\n".join(lines)


def _flatten_triplets(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        first = match.group(1).strip()
        second = match.group(2).strip()
        third = match.group(3).strip()
        return f"{first} and {second}. It also covers {third}"

    return TRIPLET_RE.sub(repl, text)


def _deformalize(text: str) -> str:
    out = text
    for old, new in BASE_REPLACEMENTS:
        out = out.replace(old, new)
        out = out.replace(old.title(), new.capitalize())
    return out


def _remove_scaffolding(text: str) -> str:
    out = text
    out = out.replace("Executive Summary", "Summary")
    out = out.replace("Current State Analysis", "Current State")
    out = out.replace("Detailed Improvement Recommendations", "Recommended Improvements")
    out = out.replace("Implementation Roadmap", "Implementation Plan")
    return out


def _rewrite_text(text: str, attempt: int, diagnosis: list[str]) -> str:
    out = text
    out = _deformalize(out)
    out = _split_long_sentences(out)
    if attempt >= 2 or "triplet cadence" in diagnosis:
        out = _flatten_triplets(out)
    if attempt >= 2 or "overly formal tone" in diagnosis:
        out = _remove_scaffolding(out)
    if attempt >= 3:
        out = out.replace("The current", "Current")
        out = out.replace("It is", "This is")
        out = out.replace("This document", "This review")
    return _normalize(out)


def _diagnose(analysis: dict[str, Any]) -> list[str]:
    summary = str(analysis.get("summary", "")).lower()
    reasons = " ".join(str(row.get("reason", "")).lower() for row in analysis.get("sentences", []))
    bag = f"{summary} {reasons}"
    diagnosis: list[str] = []

    if any(token in bag for token in ["triplet", "balanced", "symmetry"]):
        diagnosis.append("triplet cadence")
    if any(token in bag for token in ["monotone", "uniform", "smooth", "predictable"]):
        diagnosis.append("low sentence variety")
    if any(token in bag for token in ["professional", "corporate", "encyclopedic", "generic"]):
        diagnosis.append("overly formal tone")
    if any(token in bag for token in ["flawless grammar", "polish"]):
        diagnosis.append("too polished")
    if not diagnosis:
        diagnosis.append("general compression and specificity needed")
    return diagnosis


def humanize_with_retry(
    text: str,
    max_attempts: int = 3,
    min_improvement: float = 8.0,
    target_score: float = 60.0,
) -> dict[str, Any]:
    normalized = _normalize(text)
    if not normalized:
        return {
            "success": False,
            "reason": "No text submitted.",
            "baseline_analysis": analyze_text("", include_partners=False),
            "final_analysis": analyze_text("", include_partners=True),
            "humanized_text": "",
            "attempts": [],
            "improved_by": 0.0,
        }

    baseline = analyze_text(normalized, include_partners=False)
    baseline_score = float(baseline.get("score", 0.0))
    current_text = normalized
    best_text = normalized
    best_analysis = baseline
    attempts: list[dict[str, Any]] = []

    for attempt in range(1, max_attempts + 1):
        diagnosis = _diagnose(best_analysis)
        candidate = _rewrite_text(current_text, attempt=attempt, diagnosis=diagnosis)
        candidate_analysis = analyze_text(candidate, include_partners=False)
        candidate_score = float(candidate_analysis.get("score", 0.0))
        best_score = float(best_analysis.get("score", 0.0))

        attempts.append(
            {
                "attempt": attempt,
                "diagnosis": diagnosis,
                "candidate_score": candidate_score,
                "improved_vs_best": round(best_score - candidate_score, 1),
            }
        )

        if candidate_score < best_score:
            best_text = candidate
            best_analysis = candidate_analysis

        current_text = candidate

        improved_by = baseline_score - float(best_analysis.get("score", 0.0))
        if float(best_analysis.get("score", 0.0)) <= target_score or improved_by >= min_improvement:
            break

    final_full_analysis = analyze_text(best_text, include_partners=True)
    improved_by = round(baseline_score - float(best_analysis.get("score", 0.0)), 1)
    success = improved_by > 0

    return {
        "success": success,
        "reason": "Improved after retry loop." if success else "No measurable improvement after retries.",
        "baseline_analysis": baseline,
        "final_analysis": final_full_analysis,
        "humanized_text": best_text,
        "attempts": attempts,
        "improved_by": improved_by,
    }

