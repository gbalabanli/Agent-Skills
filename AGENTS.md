# Agent Configuration

## Always-Enabled Skills
- productivity/coding-momentum-coach

## Startup Behavior
On every session start, run the coding momentum analyzer with TUI display:

```bash
python productivity/coding-momentum-coach/scripts/tui_display.py
```

Or use the standard analyzer:
```bash
python productivity/coding-momentum-coach/scripts/analyze_codex_day.py --format markdown
```
