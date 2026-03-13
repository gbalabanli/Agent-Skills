---
name: copilot-image-find-and-download
description: Find and download images related to a user prompt through Copilot/Bing image discovery without requiring login. Use when the user asks for a prompt-to-image result, wants a quick downloadable image file, or specifically asks for Copilot image find-and-download behavior with output saved to ~/Downloads/temp.
---

# Copilot Image Find and Download

Use this skill to search Copilot/Bing image results from a prompt and download one selected image locally.

## Workflow

1. Capture the request.
- Use the user's text as `--prompt`.
- If the user does not choose a specific result, default to `--index 1`.

2. Run the script.
```bash
python scripts/find_and_download_copilot.py --prompt "<USER_PROMPT>"
```
- Default download location is `~/Downloads/temp`.
- Use `--index N` to pick another result from the same search page.
- Use `--filename "<name>"` for deterministic output naming.

3. Verify output.
- Confirm the script reports at least one saved image path.
- If no image is found, retry with a tighter or more descriptive prompt.

## Output Rules

- Keep downloads under `~/Downloads/temp` by default.
- Do not claim completion unless files exist on disk.
- Report exact saved file paths in the response.
- Do not require sign-in for this workflow.

## Resources

- Script: [find_and_download_copilot.py](scripts/find_and_download_copilot.py)
- Notes: [copilot-image-flow.md](references/copilot-image-flow.md)
