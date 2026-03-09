---
name: stitch-remotion-walkthrough
description: Build Stitch-based walkthrough videos and presentation-ready screen sequences with Remotion, including asset staging, screen manifests, modular compositions, and render validation. Use when Codex must turn Stitch project screens or exported screenshots into a demo video, promo walkthrough, app tour, or other screen-driven visual artifact.
---

# Stitch Remotion Walkthrough

Use this skill to turn Stitch screens or exported screenshots into a reusable Remotion walkthrough project.

## Workflow

1. Define the input source and expected output.
- Prefer existing local screenshots, manifests, or Stitch exports if they are already in the workspace.
- If the user wants a fresh pull from Stitch, discover the Stitch namespace at runtime and fetch project and screen metadata from the available MCP tools.
- Confirm whether the target output is a reusable video project, a rendered MP4, or both.

2. Stage screen assets deterministically.
- Reuse local screen images unless the user explicitly asks to refresh them.
- Save downloaded screenshots under a stable location such as `video/public/assets/screens/`.
- Record screen order, titles, durations, dimensions, and transition choices in a manifest based on [screen-manifest.example.json](templates/screen-manifest.example.json).
- Use `python scripts/download_stitch_asset.py <url> <output>` for Stitch or Google Storage asset URLs when normal fetches are flaky.

3. Reuse or create the Remotion project.
- Reuse an existing Remotion setup when `remotion.config.*`, `package.json`, or a video workspace already exists.
- Otherwise create a minimal TypeScript Remotion project in `video/` and keep generated files scoped to the walkthrough.
- Install only the dependencies needed for the requested result. Add transition packages only if the composition actually uses them.

4. Build the composition with modular files.
- Keep the project split into small files such as `ScreenSlide.tsx`, `WalkthroughComposition.tsx`, and optional overlay components.
- Start from [ScreenSlide.tsx](templates/ScreenSlide.tsx) when a slide component is needed, then adapt timing, typography, and overlays to the project.
- Treat the manifest as the source of truth for timing and ordering rather than hardcoding screen data in the component tree.
- Preserve aspect ratio and screen framing so UI screenshots do not stretch or crop accidentally.

5. Validate before finishing.
- Run the checks in [remotion-composition-checklist.md](references/remotion-composition-checklist.md).
- Preview the composition with the local Remotion workflow when dependencies are available.
- If rendering is requested, perform a smoke render and report the output path.
- If rendering cannot be completed because Stitch or Remotion is unavailable, leave the workspace in a runnable state and say what is missing.

## Output Rules

- Do not assume Stitch MCP or Remotion MCP exists; discover tools first and fall back to local files plus standard shell commands.
- Do not re-download screens if an equivalent local export already exists unless the user asks for a refresh.
- Do not collapse the whole video into one oversized component when a manifest plus small components is clearer.
- Keep filenames, screen IDs, and manifest ordering stable so later edits do not break the composition.
- Report any inferred transition timing or missing screen descriptions as assumptions.

## References

- [remotion-composition-checklist.md](references/remotion-composition-checklist.md)
- [screen-manifest.example.json](templates/screen-manifest.example.json)
- [ScreenSlide.tsx](templates/ScreenSlide.tsx)
