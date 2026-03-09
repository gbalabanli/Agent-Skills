---
name: nano-banana
description: Generate and iteratively refine images with the Gemini CLI Nano Banana extension. Use when Codex or OpenCode needs to create, edit, restyle, restore, or vary visual assets such as hero images, thumbnails, icons, diagrams, mockups, illustrations, patterns, or photo edits.
---

# Nano Banana

Use this skill for image generation work through the Gemini CLI Nano Banana extension.

## Workflow

1. Confirm the request shape.
- Identify whether the user wants `generate`, `edit`, `restore`, `icon`, `diagram`, `pattern`, or `story`.
- Extract the asset goal, target aspect ratio, style direction, and number of variations.
- If the user gives only a rough idea, turn it into one precise prompt plus one fallback variation.

2. Verify the local toolchain before first use.
- Read [setup.md](references/setup.md) if the extension has not been verified in this environment.
- Confirm `gemini` is installed, the `nanobanana` extension is available, and `GEMINI_API_KEY` is set.
- If setup is missing, stop and report the exact missing prerequisite.

3. Generate or edit with one clear command.
- Prefer the most specific slash command for the job:
  - `/generate` for text-to-image
  - `/edit` for modifying an existing image
  - `/restore` for repair and cleanup
  - `/icon` for app or UI icon work
  - `/diagram` for flows, architecture, and structured graphics
  - `/pattern` for seamless backgrounds and textures
  - `/story` for multi-frame or narrative output
- Use `gemini --yolo` so the command can run non-interactively from Codex or OpenCode.

4. Present strong first-pass prompts.
- Keep prompts concrete: subject, composition, style, lighting, palette, and exclusions.
- Add `no text` when text rendering is not desired.
- Use [prompt-patterns.md](references/prompt-patterns.md) for prompt structures by output type.

5. Iterate deliberately.
- When the user asks for changes, modify only the dimensions that changed: composition, style, palette, subject detail, or output count.
- For `try again` or `give me options`, regenerate with `--count=3`.
- For direct revisions to an existing file, prefer `/edit` over a fresh `/generate`.

6. Return the result clearly.
- Report the command used in concise form.
- Point to the output directory or generated file path.
- Note the most important tradeoff or assumption if the prompt required interpretation.

## Output Rules

- Do not claim Nano Banana is available until the local CLI and extension are verified.
- Do not route image work to another generator when this skill is explicitly requested.
- Prefer one production-quality prompt over a long brainstorm unless the user asked for options.
- Keep prompts editable and reusable; avoid overly poetic phrasing that weakens control.
- If the request is ambiguous, make one reasonable assumption and state it.

## References

- Setup and verification: [setup.md](references/setup.md)
- Prompt structures and examples: [prompt-patterns.md](references/prompt-patterns.md)
