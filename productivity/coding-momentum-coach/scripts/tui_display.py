#!/usr/bin/env python3
"""
TUI-formatted coding momentum display with progress bars and colors.
Compatible with Windows and Unix terminals.
"""
import subprocess
import json
import sys
from datetime import datetime

def run_analysis():
    """Run the analyzer and get JSON output."""
    result = subprocess.run(
        [sys.executable, "productivity/coding-momentum-coach/scripts/analyze_codex_day.py", 
         "--format", "json"],
        capture_output=True,
        text=True,
        cwd="C:/Users/Bora/Desktop/Workspace/agents/agent-skills"
    )
    return json.loads(result.stdout)

def color(text, code):
    """Add ANSI color code."""
    return f"\033[{code}m{text}\033[0m"

def progress_bar(value, max_val, width=20):
    """Create a progress bar using ASCII characters."""
    filled = int((value / max_val) * width) if max_val > 0 else 0
    bar = "=" * filled + "-" * (width - filled)
    return f"[{bar}] {value}/{max_val}"

def display_tui():
    """Display formatted TUI output."""
    try:
        data = run_analysis()
    except Exception as e:
        print(color(f"Error loading momentum data: {e}", "31"))
        return
    
    # Header using ASCII box drawing
    print()
    print(color("+==========================================================+", "36"))
    print(color("|           CODING MOMENTUM DASHBOARD                      |", "36;1"))
    print(color("+==========================================================+", "36"))
    print()
    
    # Score and Badge
    score = data.get("total_score", 0)
    badge = data.get("badge", "not-started")
    badge_colors = {
        "closer": ("105+", "35;1"),      # Magenta bold
        "builder": ("75-104", "34;1"),   # Blue bold
        "momentum": ("45-74", "32;1"),   # Green bold
        "warmup": ("15-44", "33;1"),     # Yellow bold
        "not-started": ("0-14", "37"),   # Gray
    }
    badge_label, badge_color = badge_colors.get(badge, ("?", "37"))
    
    print(f"  {color('Score:', '1')} {color(str(score), '33;1')}  {progress_bar(score, 105)}")
    print(f"  {color('Badge:', '1')} {color(badge.upper(), badge_color)} ({badge_label})")
    print()
    
    # Stats
    print(color("  [STATS]", "1"))
    print(f"     * Streak: {color(str(data.get('day_streak', 0)), '33')} days")
    print(f"     * Blocks: {data.get('qualifying_blocks', 0)} qualifying")
    print(f"     * Active: {data.get('active_minutes_estimate', 0)} minutes")
    print(f"     * Returns: {data.get('return_count', 0)} comebacks")
    print()
    
    # Current workspace
    workspace = data.get("current_workspace")
    if workspace:
        print(color("  [CURRENT WORKSPACE]", "1"))
        cwd = workspace.get("cwd", "unknown")
        if len(cwd) > 40:
            cwd = "..." + cwd[-37:]
        print(f"     {color(cwd, '90')}")
        print(f"     * Blocks: {workspace.get('qualifying_blocks', 0)}")
        print(f"     * Time: {workspace.get('active_minutes_estimate', 0)} min")
        print()
    
    # Mission
    intervention = data.get("intervention", "kickoff")
    missions = data.get("missions", [])
    if missions:
        print(color(f"  [MISSION: {intervention.upper()}]", "1"))
        print(f"     {color(missions[0], '32')}")
        print()
    
    # Prompt
    prompt = data.get("coach_prompt")
    if prompt:
        print(color("  [COACHING]", "1"))
        print(f"     {color(prompt, '90')}")
        print()
    
    # Warnings
    warnings = data.get("warnings", [])
    if warnings:
        print(color("  [!] WARNINGS", "31"))
        for w in warnings[:3]:
            print(f"     * {w}")
        print()
    
    print(color("===========================================================", "36"))
    print()

if __name__ == "__main__":
    display_tui()
