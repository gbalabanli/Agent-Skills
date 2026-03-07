---
name: coding-momentum-coach
description: Inspect same-day Codex session activity, score coding momentum across the day, detect idle drop-off, and coach the next small mission to improve consistency. Use when a user asks for a coding day status, momentum check, re-entry prompt, daily streak review, or coaching based on intra-day sessions.
---

# Coding Momentum Coach

Use this skill to turn same-day Codex sessions into a lightweight coaching loop for coding consistency.

## Workflow

1. Confirm the coaching scope.
- Default to today's activity in the local timezone.
- Default to whole-day scoring across all same-day Codex sessions.
- Also report the current workspace slice when `cwd` is available.
- If the user asks for a different date or scope, pass it explicitly to the script.

2. Run the analyzer script first.
- Use `python productivity/coding-momentum-coach/scripts/analyze_codex_day.py --format markdown --cwd <current repo path> --timezone <current timezone>` when the current timezone is available from turn context.
- Add `--date YYYY-MM-DD` when the user asks for a specific day.
- Add `--scope cwd` only when the user explicitly wants repository-local scoring.
- Let the script update the daily ledger under `~/.codex/skill-state/coding-momentum-coach/`.

3. Read the result as a coaching signal, not a productivity verdict.
- Focus on return-to-work momentum, qualifying session blocks, active minutes estimate, and streak continuity.
- Treat long idle gaps as a coaching opportunity, not a failure.
- Prefer one concrete next mission sized for `20-40 minutes`.

4. Match the intervention mode.
- `kickoff`: no qualifying work yet today; help start the first block.
- `comeback`: user is returning after an idle gap; recommend the smallest next action.
- `momentum`: user is active; keep the current chain alive without expanding scope.
- `wrapup`: day is late or user asks for closure; leave the work in a resumable state.

5. Keep the response compact and actionable.
- Report the current score, badge, streak, block count, and active minutes estimate.
- Include the current workspace contribution when available.
- Give exactly one next mission and one re-entry or wrap-up prompt.
- If warnings are present, mention them briefly without turning the response into a log dump.

## Output Rules

- Do not invent hidden productivity signals; rely on the script output.
- Do not shame the user for idle time or a low score.
- Do not recommend multiple unrelated tasks in one response.
- If there are no same-day sessions, continue in `kickoff` mode with a manual check-in style mission.
- If session parsing is partial, state that the score is provisional.

## Default Command

```bash
python productivity/coding-momentum-coach/scripts/analyze_codex_day.py --format markdown --cwd "<current repo path>" --timezone "<current timezone>"
```
