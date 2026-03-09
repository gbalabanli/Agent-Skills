# Setup

## Required Local Dependencies

- `gemini` CLI installed and available on `PATH`
- Nano Banana extension installed in Gemini CLI
- `GEMINI_API_KEY` exported in the shell environment

## Verification Commands

```bash
gemini --version
gemini extensions list
```

On Windows PowerShell, verify the API key with:

```powershell
if ($env:GEMINI_API_KEY) { "configured" } else { "missing GEMINI_API_KEY" }
```

On POSIX shells, verify with:

```bash
if [ -n "$GEMINI_API_KEY" ]; then echo "configured"; else echo "missing GEMINI_API_KEY"; fi
```

## Install the Extension

```bash
gemini extensions install https://github.com/gemini-cli-extensions/nanobanana
```

## Core Command Shapes

```bash
gemini --yolo "/generate 'prompt text here'"
gemini --yolo "/edit input.png 'change request here'"
gemini --yolo "/restore damaged-photo.jpg 'cleanup request here'"
gemini --yolo "/icon 'icon brief here'"
gemini --yolo "/diagram 'diagram brief here'"
gemini --yolo "/pattern 'pattern brief here'"
gemini --yolo "/story 'story brief here'"
```

## Useful Option Patterns

Use these inside the quoted Nano Banana command when supported by the installed extension:

```text
--count=3
--preview
--aspect=16:9
--styles="editorial,clean"
--format=grid
```

## Notes for Codex and OpenCode

- Prefer non-interactive commands so the agent can run them without follow-up prompts.
- Keep output in a deterministic working directory such as `./nanobanana-output/`.
- If the extension version differs from the examples above, inspect `gemini extensions list` or the extension help output and adjust the command shape instead of guessing.
