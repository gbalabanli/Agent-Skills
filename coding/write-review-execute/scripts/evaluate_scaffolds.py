#!/usr/bin/env python3
"""Evaluate three scaffolds with optional command execution and weighted scoring.

Spec format (JSON):
{
  "mode": "proof-of-concept" | "theoretical-only",
  "timeout_sec": 120,
  "correctness_gate": 0.60,
  "weights": {
    "correctness": 0.40,
    "execution_evidence": 0.20,
    "maintainability": 0.20,
    "complexity": 0.10,
    "performance_risk": 0.10
  },
  "alternatives": [
    {
      "id": "A",
      "name": "Option A",
      "cwd": ".",
      "command": "pytest -q",
      "review_scores": {
        "correctness": 0.82,
        "maintainability": 0.73,
        "complexity": 0.66,
        "performance_risk": 0.70
      }
    }
  ]
}
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_WEIGHTS = {
    "correctness": 0.40,
    "execution_evidence": 0.20,
    "maintainability": 0.20,
    "complexity": 0.10,
    "performance_risk": 0.10,
}

CORE_REVIEW_KEYS = ("correctness", "maintainability", "complexity", "performance_risk")
VALID_MODES = {"theoretical-only", "proof-of-concept"}


@dataclass
class CommandResult:
    status: str
    returncode: int | None
    output_summary: str
    execution_evidence_score: float


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def load_json(path: Path) -> dict[str, Any]:
    try:
        # Accept UTF-8 BOM because Windows PowerShell commonly writes it by default.
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        raise ValueError(f"Spec file not found: {path}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in spec file: {exc}") from exc


def normalize_weights(raw_weights: dict[str, Any] | None) -> dict[str, float]:
    weights = dict(DEFAULT_WEIGHTS)
    if raw_weights:
        for key, val in raw_weights.items():
            if key not in weights:
                raise ValueError(f"Unknown weight key: {key}")
            try:
                weights[key] = float(val)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Weight must be numeric for '{key}'") from exc

    total = sum(weights.values())
    if total <= 0:
        raise ValueError("Weight sum must be positive")
    return {k: v / total for k, v in weights.items()}


def read_review_scores(alt: dict[str, Any]) -> dict[str, float]:
    raw = alt.get("review_scores")
    if not isinstance(raw, dict):
        raise ValueError(f"Alternative '{alt.get('id', '?')}' missing review_scores object")
    scores: dict[str, float] = {}
    for key in CORE_REVIEW_KEYS:
        if key not in raw:
            raise ValueError(f"Alternative '{alt.get('id', '?')}' missing review score '{key}'")
        try:
            scores[key] = clamp01(float(raw[key]))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Alternative '{alt.get('id', '?')}' has non-numeric review score '{key}'"
            ) from exc
    return scores


def summarize_output(stdout: str, stderr: str, preview_lines: int) -> str:
    combined = []
    if stdout.strip():
        combined.extend(stdout.strip().splitlines())
    if stderr.strip():
        combined.extend(stderr.strip().splitlines())

    if not combined:
        return "(no output)"
    excerpt = combined[:preview_lines]
    if len(combined) > preview_lines:
        excerpt.append("... (truncated)")
    return "\n".join(excerpt)


def run_command(
    command: str,
    cwd: Path,
    timeout_sec: float,
    preview_lines: int,
) -> CommandResult:
    try:
        completed = subprocess.run(
            command,
            shell=True,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
        summary = summarize_output(completed.stdout, completed.stderr, preview_lines)
        if completed.returncode == 0:
            return CommandResult("pass", 0, summary, 1.0)
        return CommandResult("fail", completed.returncode, summary, 0.20)
    except subprocess.TimeoutExpired as exc:
        summary = summarize_output(exc.stdout or "", exc.stderr or "", preview_lines)
        return CommandResult("timeout", None, summary, 0.0)
    except OSError as exc:
        return CommandResult("error", None, str(exc), 0.0)


def evaluate_alternative(
    alt: dict[str, Any],
    mode: str,
    timeout_sec: float,
    preview_lines: int,
    correctness_gate: float,
    repo_root: Path,
    weights: dict[str, float],
) -> dict[str, Any]:
    alt_id = str(alt.get("id") or alt.get("name") or "unknown")
    name = str(alt.get("name") or alt_id)
    scores = read_review_scores(alt)

    if mode == "theoretical-only":
        cmd_result = CommandResult(
            status="skipped",
            returncode=None,
            output_summary="Execution skipped by mode (theoretical-only).",
            execution_evidence_score=0.50,
        )
    else:
        command = alt.get("command")
        if not isinstance(command, str) or not command.strip():
            cmd_result = CommandResult(
                status="not-run",
                returncode=None,
                output_summary="No command provided for proof-of-concept mode.",
                execution_evidence_score=0.0,
            )
        else:
            cwd_value = alt.get("cwd", ".")
            cwd = (repo_root / str(cwd_value)).resolve()
            cmd_result = run_command(command, cwd, timeout_sec, preview_lines)

    weighted_inputs = {
        "correctness": scores["correctness"],
        "execution_evidence": cmd_result.execution_evidence_score,
        "maintainability": scores["maintainability"],
        "complexity": scores["complexity"],
        "performance_risk": scores["performance_risk"],
    }
    weighted_score = sum(weights[key] * weighted_inputs[key] for key in weights)

    gate_reasons = []
    if scores["correctness"] < correctness_gate:
        gate_reasons.append(f"correctness<{correctness_gate:.2f}")
    if mode == "proof-of-concept" and cmd_result.status != "pass":
        gate_reasons.append("execution_not_pass")
    gate_failed = len(gate_reasons) > 0

    return {
        "id": alt_id,
        "name": name,
        "scores": weighted_inputs,
        "weighted_score": round(weighted_score, 4),
        "gate_failed": gate_failed,
        "gate_reasons": gate_reasons,
        "execution": {
            "status": cmd_result.status,
            "returncode": cmd_result.returncode,
            "output_summary": cmd_result.output_summary,
            "command": alt.get("command"),
            "cwd": alt.get("cwd", "."),
        },
    }


def sensitivity_note(results: list[dict[str, Any]], weights: dict[str, float]) -> str:
    if len(results) < 2:
        return "Not enough alternatives for sensitivity check."

    top_criteria = sorted(weights.items(), key=lambda kv: kv[1], reverse=True)[:2]
    baseline_order = [row["id"] for row in sorted(results, key=lambda r: r["weighted_score"], reverse=True)]

    def rerank(mutated: dict[str, float]) -> list[str]:
        order = []
        rescored = []
        for row in results:
            score = sum(mutated[k] * row["scores"][k] for k in mutated)
            rescored.append((row["id"], score))
        for item in sorted(rescored, key=lambda x: x[1], reverse=True):
            order.append(item[0])
        return order

    for criterion, base in top_criteria:
        for delta in (1.2, 0.8):
            mutated = dict(weights)
            mutated[criterion] = base * delta
            total = sum(mutated.values())
            mutated = {k: v / total for k, v in mutated.items()}
            if rerank(mutated) != baseline_order:
                return "Rank flip detected under +/-20% weight perturbation."

    return "Ranking stable under +/-20% perturbation on top-weight criteria."


def render_markdown_summary(payload: dict[str, Any]) -> str:
    lines = []
    lines.append(f"Mode: `{payload['mode']}`")
    lines.append("")
    lines.append("| id | name | weighted_score | gate_failed | execution_status |")
    lines.append("|---|---|---:|---|---|")
    for row in payload["ranked"]:
        lines.append(
            f"| {row['id']} | {row['name']} | {row['weighted_score']:.4f} | "
            f"{str(row['gate_failed']).lower()} | {row['execution']['status']} |"
        )
    lines.append("")
    lines.append(f"Sensitivity: {payload['sensitivity_note']}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate three code scaffolds with weighted scoring.")
    parser.add_argument("--spec", required=True, help="Path to evaluation JSON spec.")
    parser.add_argument("--json-out", help="Optional path to write JSON result.")
    parser.add_argument("--md-out", help="Optional path to write Markdown summary.")
    parser.add_argument(
        "--preview-lines",
        type=int,
        default=12,
        help="Number of output lines to retain per command summary.",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root used to resolve alternative cwd values.",
    )
    args = parser.parse_args()

    try:
        spec = load_json(Path(args.spec))
        mode = str(spec.get("mode", "proof-of-concept"))
        if mode not in VALID_MODES:
            raise ValueError(
                f"Invalid mode '{mode}'. Expected one of: {', '.join(sorted(VALID_MODES))}"
            )

        alternatives = spec.get("alternatives")
        if not isinstance(alternatives, list):
            raise ValueError("Spec field 'alternatives' must be a list")
        if len(alternatives) != 3:
            raise ValueError("Spec must include exactly 3 alternatives")

        timeout_sec = float(spec.get("timeout_sec", 120))
        correctness_gate = clamp01(float(spec.get("correctness_gate", 0.60)))
        weights = normalize_weights(spec.get("weights"))
        repo_root = Path(args.repo_root).resolve()

        evaluated = [
            evaluate_alternative(
                alt=alt,
                mode=mode,
                timeout_sec=timeout_sec,
                preview_lines=args.preview_lines,
                correctness_gate=correctness_gate,
                repo_root=repo_root,
                weights=weights,
            )
            for alt in alternatives
        ]

        ranked = sorted(
            evaluated,
            key=lambda row: (row["gate_failed"], -row["weighted_score"], row["id"]),
        )
        payload = {
            "mode": mode,
            "weights": weights,
            "correctness_gate": correctness_gate,
            "ranked": ranked,
            "sensitivity_note": sensitivity_note(ranked, weights),
        }

        output = json.dumps(payload, indent=2)
        print(output)

        if args.json_out:
            Path(args.json_out).write_text(output + "\n", encoding="utf-8")
        if args.md_out:
            Path(args.md_out).write_text(
                render_markdown_summary(payload) + "\n",
                encoding="utf-8",
            )

        return 0
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
