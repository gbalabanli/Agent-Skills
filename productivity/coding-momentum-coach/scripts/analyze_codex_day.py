from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, asdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

IDLE_GAP_MINUTES = 45
ACTIVE_GAP_CAP_MINUTES = 10


def configure_output_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(errors="replace")
            except Exception:
                pass


@dataclass(frozen=True)
class Event:
    timestamp: datetime
    session_id: str
    kind: str
    cwd: str | None
    message: str | None = None


@dataclass(frozen=True)
class Block:
    start: datetime
    end: datetime
    session_ids: list[str]
    event_count: int
    user_messages: int
    productive_events: int
    task_complete_count: int
    active_minutes_estimate: int
    qualifies: bool
    comeback_gap_minutes: int | None
    recent_message: str | None
    cwd_counts: dict[str, int]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze same-day Codex sessions and emit coding momentum coaching."
    )
    parser.add_argument("--date", dest="target_date", help="Target local date in YYYY-MM-DD format.")
    parser.add_argument("--timezone", default=None, help="IANA timezone. Defaults to local timezone.")
    parser.add_argument(
        "--sessions-root",
        default=str(Path("~/.codex/sessions").expanduser()),
        help="Root folder that contains Codex session JSONL files.",
    )
    parser.add_argument(
        "--state-dir",
        default=str(Path("~/.codex/skill-state/coding-momentum-coach").expanduser()),
        help="Directory where daily ledger files are stored.",
    )
    parser.add_argument(
        "--scope",
        choices=("global", "cwd"),
        default="global",
        help="Whether to score all same-day sessions or only the selected cwd.",
    )
    parser.add_argument(
        "--cwd",
        default=str(Path.cwd()),
        help="Current workspace path used for the repo-local slice.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="markdown",
        help="Output format.",
    )
    return parser.parse_args()


def detect_timezone(name: str | None) -> ZoneInfo:
    if name:
        return ZoneInfo(name)

    env_tz = os.environ.get("TZ")
    if env_tz:
        try:
            return ZoneInfo(env_tz)
        except Exception:
            pass

    local = datetime.now().astimezone().tzinfo
    if isinstance(local, ZoneInfo):
        return local

    local_name = getattr(local, "key", None) or str(local)
    try:
        return ZoneInfo(local_name)
    except Exception:
        return ZoneInfo("UTC")


def parse_target_date(value: str | None, tz: ZoneInfo) -> date:
    if not value:
        return datetime.now(tz).date()
    return date.fromisoformat(value)


def normalize_cwd(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return str(Path(value).expanduser().resolve()).lower()
    except OSError:
        return str(Path(value).expanduser()).lower()


def sessions_day_dir(root: Path, target: date) -> Path:
    return root / f"{target.year:04d}" / f"{target.month:02d}" / f"{target.day:02d}"


def parse_event_timestamp(raw: str, tz: ZoneInfo) -> datetime:
    return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(tz)


def load_events(
    day_dir: Path, tz: ZoneInfo, warnings: list[str], target: date
) -> tuple[list[Event], dict[str, str | None]]:
    events: list[Event] = []
    session_cwds: dict[str, str | None] = {}

    if not day_dir.exists():
        warnings.append(f"Session directory not found for {target.isoformat()}: {day_dir}")
        return events, session_cwds

    files = sorted(day_dir.glob("*.jsonl"))
    if not files:
        warnings.append(f"No session files found for {target.isoformat()} in {day_dir}")
        return events, session_cwds

    for file_path in files:
        current_session_id: str | None = None
        current_cwd: str | None = None
        for line_no, raw_line in enumerate(file_path.read_text(encoding="utf-8").splitlines(), start=1):
            if not raw_line.strip():
                continue
            try:
                payload = json.loads(raw_line)
            except json.JSONDecodeError as exc:
                warnings.append(f"{file_path.name}:{line_no} invalid JSON skipped: {exc.msg}")
                continue

            record_type = payload.get("type")
            timestamp = payload.get("timestamp")
            if record_type == "session_meta":
                current_session_id = payload.get("payload", {}).get("id") or current_session_id
                session_cwds.setdefault(current_session_id or file_path.stem, current_cwd)
                continue

            if record_type == "turn_context":
                current_session_id = current_session_id or file_path.stem
                current_cwd = normalize_cwd(payload.get("payload", {}).get("cwd"))
                session_cwds[current_session_id] = current_cwd
                continue

            if not timestamp:
                continue

            session_id = current_session_id or file_path.stem
            event_time = parse_event_timestamp(timestamp, tz)
            if event_time.date() != target:
                continue

            if record_type == "event_msg":
                message_type = payload.get("payload", {}).get("type")
                message = payload.get("payload", {}).get("message")
                if message_type in {"user_message", "agent_message", "task_complete"}:
                    events.append(
                        Event(
                            timestamp=event_time,
                            session_id=session_id,
                            kind=message_type,
                            cwd=current_cwd or session_cwds.get(session_id),
                            message=message,
                        )
                    )
                continue

            if record_type == "response_item":
                item_type = payload.get("payload", {}).get("type")
                if item_type in {"function_call", "function_call_output"}:
                    events.append(
                        Event(
                            timestamp=event_time,
                            session_id=session_id,
                            kind=item_type,
                            cwd=current_cwd or session_cwds.get(session_id),
                        )
                    )

    events.sort(key=lambda event: event.timestamp)
    return events, session_cwds


def build_blocks(events: list[Event]) -> list[Block]:
    if not events:
        return []

    blocks: list[list[Event]] = []
    current: list[Event] = [events[0]]
    for event in events[1:]:
        previous = current[-1]
        gap_minutes = int((event.timestamp - previous.timestamp).total_seconds() // 60)
        if gap_minutes >= IDLE_GAP_MINUTES:
            blocks.append(current)
            current = [event]
        else:
            current.append(event)
    blocks.append(current)

    rendered: list[Block] = []
    previous_end: datetime | None = None
    for raw_block in blocks:
        active_minutes = 0
        for earlier, later in zip(raw_block, raw_block[1:]):
            gap = later.timestamp - earlier.timestamp
            capped = min(gap, timedelta(minutes=ACTIVE_GAP_CAP_MINUTES))
            active_minutes += int(capped.total_seconds() // 60)

        user_messages = sum(1 for event in raw_block if event.kind == "user_message")
        productive_events = sum(
            1
            for event in raw_block
            if event.kind in {"function_call", "function_call_output", "task_complete"}
        )
        task_complete_count = sum(1 for event in raw_block if event.kind == "task_complete")
        recent_message = next(
            (event.message for event in reversed(raw_block) if event.kind == "user_message" and event.message),
            None,
        )

        cwd_counts: dict[str, int] = {}
        for event in raw_block:
            if event.cwd:
                cwd_counts[event.cwd] = cwd_counts.get(event.cwd, 0) + 1

        comeback_gap_minutes: int | None = None
        if previous_end is not None:
            comeback_gap_minutes = int((raw_block[0].timestamp - previous_end).total_seconds() // 60)

        qualifies = (
            user_messages >= 1 and productive_events >= 1 and active_minutes >= 5
        )
        rendered.append(
            Block(
                start=raw_block[0].timestamp,
                end=raw_block[-1].timestamp,
                session_ids=sorted({event.session_id for event in raw_block}),
                event_count=len(raw_block),
                user_messages=user_messages,
                productive_events=productive_events,
                task_complete_count=task_complete_count,
                active_minutes_estimate=active_minutes,
                qualifies=qualifies,
                comeback_gap_minutes=comeback_gap_minutes,
                recent_message=recent_message,
                cwd_counts=cwd_counts,
            )
        )
        previous_end = raw_block[-1].timestamp

    return rendered


def score_blocks(blocks: list[Block]) -> tuple[int, list[dict[str, Any]]]:
    score = 0
    scored_blocks: list[dict[str, Any]] = []
    qualifying_seen = 0
    comeback_awards = 0

    for block in blocks:
        breakdown = {
            "start": block.start.isoformat(),
            "end": block.end.isoformat(),
            "qualifies": block.qualifies,
            "active_minutes_estimate": block.active_minutes_estimate,
            "awards": [],
        }
        if not block.qualifies:
            scored_blocks.append(breakdown)
            continue

        qualifying_seen += 1
        if qualifying_seen == 1:
            score += 15
            breakdown["awards"].append({"name": "first-block", "points": 15})
        else:
            if qualifying_seen <= 5:
                score += 10
                breakdown["awards"].append({"name": "extra-block", "points": 10})
            if comeback_awards < 3:
                score += 20
                breakdown["awards"].append({"name": "comeback", "points": 20})
                comeback_awards += 1

        if block.active_minutes_estimate >= 40:
            score += 10
            breakdown["awards"].append({"name": "deep-block", "points": 10})
        elif block.active_minutes_estimate >= 20:
            score += 5
            breakdown["awards"].append({"name": "steady-block", "points": 5})

        if block.task_complete_count >= 1:
            score += 5
            breakdown["awards"].append({"name": "completion", "points": 5})

        scored_blocks.append(breakdown)

    return score, scored_blocks


def pick_badge(score: int) -> str:
    if score >= 105:
        return "closer"
    if score >= 75:
        return "builder"
    if score >= 45:
        return "momentum"
    if score >= 15:
        return "warmup"
    return "not-started"


def recent_topic(blocks: list[Block]) -> str:
    for block in reversed(blocks):
        if block.recent_message:
            return " ".join(block.recent_message.strip().split())[:140]
    return "the next concrete coding step"


def clean_topic(topic: str) -> str:
    normalized = " ".join(topic.strip().split())
    normalized = normalized.rstrip(" .,:;!?")
    return normalized or "the next concrete coding step"


def select_intervention(
    target: date, tz: ZoneInfo, blocks: list[Block], qualifying_blocks: list[Block]
) -> str:
    now_local = datetime.now(tz)
    if not qualifying_blocks:
        return "kickoff"
    latest_block = qualifying_blocks[-1]
    latest_gap_minutes = int((now_local - latest_block.end).total_seconds() // 60)
    if target == now_local.date() and latest_gap_minutes >= IDLE_GAP_MINUTES:
        return "comeback"
    if target < now_local.date() or now_local.hour >= 18:
        return "wrapup"
    return "momentum"


def build_mission(intervention: str, topic: str, score: int) -> tuple[str, str]:
    topic = clean_topic(topic)
    next_badge = (
        "warmup" if score < 15 else
        "momentum" if score < 45 else
        "builder" if score < 75 else
        "closer" if score < 105 else
        "closer"
    )

    if intervention == "kickoff":
        mission = f"Start a 25 minute block on {topic}. Leave one visible artifact: code change, note, or test."
        prompt = f"Open the smallest next step for {topic} and ship one checkpoint before switching context."
        return mission, prompt
    if intervention == "comeback":
        mission = f"Spend 20-30 minutes resuming {topic}. Prioritize the smallest action that gets you moving again."
        prompt = f"You are one qualifying block away from stronger day momentum. Resume {topic} and aim for the next badge: {next_badge}."
        return mission, prompt
    if intervention == "wrapup":
        mission = f"Use 20 minutes to close the loop on {topic}: leave notes, a checkpoint commit, or the next-step marker."
        prompt = f"Do one clean finishing move on {topic} so tomorrow starts from motion, not re-discovery."
        return mission, prompt

    mission = f"Stay on {topic} for another 30 minutes and finish one clearly bounded checkpoint."
    prompt = f"Momentum is already live. Keep scope narrow on {topic} and convert the current block into a visible win."
    return mission, prompt


def compute_streak(state_dir: Path, target: date, qualifies_today: bool) -> int:
    if not qualifies_today:
        return 0

    streak = 1
    cursor = target - timedelta(days=1)
    while True:
        ledger_path = state_dir / f"{cursor.isoformat()}.json"
        if not ledger_path.exists():
            break
        try:
            payload = json.loads(ledger_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            break
        if int(payload.get("qualifying_blocks", 0)) < 1:
            break
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def summarize_cwd(events: list[Event], target_cwd: str | None) -> dict[str, Any] | None:
    if not target_cwd:
        return None

    scoped = [event for event in events if event.cwd == target_cwd]
    if not scoped:
        return {
            "cwd": target_cwd,
            "event_count": 0,
            "qualifying_blocks": 0,
            "active_minutes_estimate": 0,
        }

    blocks = build_blocks(scoped)
    qualifying = [block for block in blocks if block.qualifies]
    return {
        "cwd": target_cwd,
        "event_count": len(scoped),
        "qualifying_blocks": len(qualifying),
        "active_minutes_estimate": sum(block.active_minutes_estimate for block in qualifying),
    }


def build_cwd_breakdown(events: list[Event]) -> dict[str, dict[str, int]]:
    grouped: dict[str, list[Event]] = {}
    for event in events:
        if event.cwd:
            grouped.setdefault(event.cwd, []).append(event)

    breakdown: dict[str, dict[str, int]] = {}
    for cwd, cwd_events in grouped.items():
        blocks = build_blocks(cwd_events)
        qualifying = [block for block in blocks if block.qualifies]
        breakdown[cwd] = {
            "event_count": len(cwd_events),
            "qualifying_blocks": len(qualifying),
            "active_minutes_estimate": sum(block.active_minutes_estimate for block in qualifying),
        }
    return breakdown


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        f"Day summary: {summary['intervention']} mode for {summary['date']} with score {summary['total_score']} and badge {summary['badge']}.",
        "",
        "Scoreboard",
        f"- Streak: {summary['day_streak']}",
        f"- Qualifying blocks: {summary['qualifying_blocks']}",
        f"- Return count: {summary['return_count']}",
        f"- Active minutes estimate: {summary['active_minutes_estimate']}",
    ]

    repo_slice = summary.get("current_workspace")
    if repo_slice:
        lines.append(
            f"- Current workspace: {repo_slice['qualifying_blocks']} qualifying blocks, "
            f"{repo_slice['active_minutes_estimate']} active minutes estimate"
        )

    lines.extend(
        [
            "",
            "Next mission",
            f"- {summary['missions'][0]}",
            "",
            "Prompt",
            f"- {summary['coach_prompt']}",
        ]
    )

    warnings = summary.get("warnings") or []
    if warnings:
        lines.extend(["", "Warnings"])
        for warning in warnings[:5]:
            lines.append(f"- {warning}")

    return "\n".join(lines)


def serialize_block(block: Block) -> dict[str, Any]:
    payload = asdict(block)
    payload["start"] = block.start.isoformat()
    payload["end"] = block.end.isoformat()
    return payload


def write_ledger(state_dir: Path, target: date, summary: dict[str, Any]) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = state_dir / f"{target.isoformat()}.json"
    ledger_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")


def main() -> int:
    configure_output_streams()
    args = parse_args()
    timezone = detect_timezone(args.timezone)
    target = parse_target_date(args.target_date, timezone)
    sessions_root = Path(args.sessions_root).expanduser()
    state_dir = Path(args.state_dir).expanduser()
    target_cwd = normalize_cwd(args.cwd)

    warnings: list[str] = []
    day_dir = sessions_day_dir(sessions_root, target)
    events, _ = load_events(day_dir, timezone, warnings, target)

    filtered_events = events
    if args.scope == "cwd" and target_cwd:
        filtered_events = [event for event in events if event.cwd == target_cwd]

    blocks = build_blocks(filtered_events)
    qualifying_blocks = [block for block in blocks if block.qualifies]
    total_score, scored_blocks = score_blocks(blocks)
    intervention = select_intervention(target, timezone, blocks, qualifying_blocks)
    topic = recent_topic(blocks)
    mission, coach_prompt = build_mission(intervention, topic, total_score)
    return_count = sum(
        1
        for block in qualifying_blocks[1:]
        if (block.comeback_gap_minutes or 0) >= IDLE_GAP_MINUTES
    )
    active_minutes = sum(block.active_minutes_estimate for block in qualifying_blocks)
    session_ids = sorted({event.session_id for event in filtered_events})
    cwd_breakdown = build_cwd_breakdown(events)
    streak = compute_streak(state_dir, target, bool(qualifying_blocks))

    summary: dict[str, Any] = {
        "date": target.isoformat(),
        "timezone": timezone.key,
        "scope": args.scope,
        "total_score": total_score,
        "badge": pick_badge(total_score),
        "day_streak": streak,
        "qualifying_blocks": len(qualifying_blocks),
        "return_count": return_count,
        "active_minutes_estimate": active_minutes,
        "session_ids": session_ids,
        "cwd_breakdown": cwd_breakdown,
        "last_intervention_type": intervention,
        "intervention": intervention,
        "missions": [mission],
        "coach_prompt": coach_prompt,
        "current_workspace": summarize_cwd(events, target_cwd),
        "warnings": warnings,
        "blocks": [serialize_block(block) for block in blocks],
        "scored_blocks": scored_blocks,
    }

    write_ledger(state_dir, target, summary)

    if args.format == "json":
        json.dump(summary, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render_markdown(summary))
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
