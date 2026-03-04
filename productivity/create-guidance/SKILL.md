---
name: create-guidance
description: Clarify vague or high-level requests, propose options, and give direct step-by-step guidance. Use when a user asks for help understanding what to do, how to do it, or needs intent clarification to turn a goal into actionable steps.
---

# Create Guidance

## Overview

Turn unclear goals into clear, actionable guidance by confirming intent, offering options, and explaining a recommended path with concrete steps.

## Workflow

### 1) Triage the request

- Identify the user's goal, scope, constraints, and success criteria.
- Restate the intent in one sentence to confirm understanding.

### 1b) Self-check to reduce misunderstanding (anti-hallucination)

- Score your understanding `0-5`:
  - `0-1`: You do not know what the user wants.
  - `2`: You have a rough guess, but multiple plausible intents exist.
  - `3`: You mostly understand, but key constraints/inputs are missing.
  - `4`: You understand intent and constraints; only minor details missing.
  - `5`: You understand intent, constraints, and success criteria clearly.
- If score `<= 3`, ask clarifying questions before proposing a detailed solution.
- If score `>= 4`, proceed, but still call out any assumptions explicitly.

### 2) Ask minimal clarifying questions (only if needed)

- Ask 1-3 targeted questions that unblock action.
- If safe assumptions are possible, state them and proceed.

**Clarifying question template (pick 1-3):**
- Goal: "What outcome should we optimize for (speed, correctness, cost, UX)?"
- Scope: "What's in/out of scope?"
- Inputs: "What files/URLs/examples should I use? Paste a sample."
- Constraints: "Any deadlines, platform limits, or libraries to avoid?"
- Success: "What does 'done' look like (tests, screenshot, metric, behavior)?"

### 3) Propose options

- Offer 2-3 realistic options with tradeoffs (time, cost, complexity, risk).
- Recommend one option based on stated constraints.

### 4) Give direct, step-by-step guidance

- Provide ordered steps the user can follow immediately.
- Include prerequisites, tools, and checkpoints when useful.

### 5) Close the loop

- Ask for missing inputs after presenting an initial path.
- Offer to refine once the user answers.

## Response structure

- Summarize intent in one sentence.
- State assumptions (if any).
- List options (2-3 bullets).
- Recommend one path in 1-2 sentences.
- Provide numbered steps.

## Notes

- Keep guidance concrete and actionable; avoid vague advice.
- Match the user's level; explain jargon briefly if it appears.
- If the request is infeasible or unsafe, explain why and offer a safe alternative.
