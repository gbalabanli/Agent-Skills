---
name: humanize-text
description: Rewrite AI-sounding text so it reads naturally, specifically, and credibly without changing the underlying meaning. Use when users ask to humanize text, make writing less robotic, remove AI patterns, soften corporate phrasing, preserve facts while improving flow, or revise copy that was flagged by an AI detector.
---

# Humanize Text

Use this skill to turn stiff or obviously AI-shaped writing into clean human prose without drifting from the source.

## Workflow

1. Classify the rewrite target before changing anything.
- Identify the text type: `marketing`, `email`, `essay`, `article`, `technical`, `social`, or `general`.
- Identify the requested rewrite intensity: `light`, `standard`, or `strong`.
- Identify hard constraints: tone, length, audience, format, required phrases, citations, links, and terminology.
- If the user supplied detector output, treat it as a hint, not proof.

2. Preserve what must not move.
- Keep facts, numbers, dates, names, claims, links, and quoted language unless the user explicitly asked to rewrite them.
- Preserve structure when structure is functional, such as bullets, headings, steps, or compliance wording.
- Keep domain terminology when simplification would reduce precision.
- If the source is already personal or opinionated, preserve that voice instead of flattening it.

3. Remove high-risk AI patterns first.
- Cut inflated significance claims, vague authority phrases, and generic scene-setting.
- Replace padded adjective stacks with one concrete claim.
- Remove filler transitions and summary lines that say little.
- Collapse repetitive sentence shapes and over-explained connectors.
- Replace generic abstractions with concrete nouns, verbs, and specifics already present in the text.
- Use [ai-patterns.md](references/ai-patterns.md) as the checklist.

4. Rebuild the prose in the right mode.
- Use [rewrite-modes.md](references/rewrite-modes.md) to match the genre.
- `light`: tighten wording, vary cadence, remove obvious tells, keep structure nearly intact.
- `standard`: rewrite most sentences for natural flow while preserving structure and meaning.
- `strong`: reorganize locally, compress repetition, and sharpen voice, but still preserve claims and scope.
- Do not "humanize" by adding slang, fake mistakes, fake anecdotes, or unsupported opinions.

5. Run a credibility pass.
- Read the rewrite against the source and confirm that no fact, qualifier, or caveat disappeared.
- Remove any new claims, emotional framing, or implied authority not grounded in the source.
- Check whether the result sounds like a competent person wrote it, not a detector-avoidance gimmick.
- If the rewrite still sounds synthetic, make it more specific, shorter, and less symmetrical.

6. Deliver the result in the smallest useful format.
- By default, return the rewritten text first.
- Add a brief change summary only when it helps the user understand the tradeoffs.
- If the user asked for detector-oriented help, call out the patterns removed instead of promising a score.
7. If scoring is requested, run a retry loop.
- Score the original text first.
- Humanize and score again.
- If score does not improve enough, diagnose likely causes from detector feedback (e.g., monotone cadence, triplet phrasing, corporate tone) and retry humanization.
- Stop after a bounded number of retries and return the best-scoring rewrite with a short retry log.

## Rewrite Rules

- Prefer specificity over polish.
- Prefer direct verbs over abstract nouns.
- Prefer natural sentence length variation over perfectly even rhythm.
- Keep emphasis rare and earned.
- Keep transitions minimal; move directly to the next point when possible.
- Keep personality appropriate to the genre. Technical docs and formal emails should not sound like personal essays.
- Do not manufacture "human" traits such as typos, emoji clutter, forced humor, or fake vulnerability.
- Do not claim detector safety or guarantee a text will pass any AI checker.

## Output Rules

- If the user asked only for a rewrite, provide the rewrite without a long preamble.
- If there are preservation risks, state them briefly before rewriting.
- If the source is too short for meaningful humanization, say so and apply only a light pass.
- If the source is formal, optimize for credibility and clarity, not personality.
- If the source is personal or editorial, allow more rhythm and voice, but keep it grounded in the original meaning.

## References

- [ai-patterns.md](references/ai-patterns.md)
- [rewrite-modes.md](references/rewrite-modes.md)

## Local Tools

- Launch the local detector UI with `python scripts/serve_ui.py`.
- Use the app in `ui/` to paste full text, fetch live `AiDetector.com`, `QuillBot`, and `Scribbr` scores, and run `Humanize + Recheck` for automatic retry-based humanization with before/after scoring.
- Treat external detector scores as advisory signals. Do not represent them as proof.
