---
name: web-deepsearch
description: Perform deep web research for complex questions that require decomposition, multi-query coverage, evidence ranking, contradiction handling, and practical recommendations with citations. Use when the user asks to compare options, evaluate tradeoffs, design architecture or integration strategy, select tools or vendors, or needs high-confidence research beyond quick lookup.
---

# Web Deep Research

## Scope
- Research external knowledge from web sources.
- For project-internal codebase questions, use local file analysis workflows instead.
- Prefer primary sources first (official docs, standards, papers, vendor docs).
- Use community and blog sources as supporting evidence, not anchors.

## Phase 1: Frame the Problem
1. Rewrite the user question into one decision statement.
2. Define the output type: compare, choose, explain, plan, or risk review.
3. Decompose into 3-5 sub-questions that collectively answer the full request.
4. Note explicit constraints: budget, timeline, scale, compliance, and environment.

## Phase 2: Generate the Search Plan
For each sub-question, create 3-5 query variants:
- Baseline query
- Official-doc query (`site:docs...` or vendor domain)
- Comparison query (`X vs Y`)
- Risk or limitation query
- Recent-update query (`after:YYYY`)

Rules:
- Build 12-20 total queries.
- Run in parallel batches of 4-8 queries.
- If results are weak, re-query only missing gaps with targeted follow-ups.

## Phase 3: Collect and Rank Evidence
1. Merge all results.
2. Deduplicate by URL, domain, and content overlap.
3. Rank each source on:
   - Credibility (0-10): official docs, standards, papers > vendor blogs > forums.
   - Freshness (0-10): newer sources score higher when topic changes quickly.
   - Relevance (0-10): direct answers with implementation detail score highest.
4. Compute weighted quality score:
   `score = credibility*0.5 + freshness*0.2 + relevance*0.3`
5. Keep highest-quality sources and drop low-value duplicates.

Target evidence quality:
- At least 8 solid sources for complex requests.
- At least 50% authoritative sources.
- At least 30% recent sources for fast-moving topics.

## Phase 4: Synthesize Findings
For each sub-question:
- Summarize what sources agree on.
- Highlight disagreements and explain why they differ (context, date, assumptions).
- Extract practical implications (cost, complexity, performance, risk).

Cross-question synthesis:
- Connect findings across sub-questions.
- Identify decision drivers and blocking unknowns.
- Separate "known with confidence" from "needs validation".

## Phase 5: Produce Decision-Ready Output
Use this structure:

```markdown
# Deep Research: <Question>

## Executive Summary
2-3 short paragraphs with the main answer and rationale.

## Research Overview
- Sub-questions: <n>
- Queries executed: <n>
- Sources used: <n> (<authoritative %>, <recent %>)
- Iterations: <n>

## Findings
### 1) <Sub-question>
Narrative synthesis with citations [1][2].
- Key insight
- Key insight
- Key insight

### 2) <Sub-question>
...

## Synthesis
- Consensus points
- Contradictions and context
- Remaining uncertainty

## Recommendations
### Critical
1. <Action + why + evidence>
2. <Action + why + evidence>

### Important
1. <Action + why + evidence>
2. <Action + why + evidence>

### Optional
1. <Action + why + evidence>

## Sources
[1] Title - Organization, Date. URL
[2] Title - Organization, Date. URL
```

Output rules:
- Every factual claim must map to citations.
- Recommendations must be actionable and prioritized.
- Explicitly list assumptions when evidence is incomplete.

## Phase 6: Refine
Run at least one gap check before finalizing:
- Any sub-question with fewer than 3 meaningful citations?
- Any major contradiction not explained?
- Is guidance still ambiguous for next-step execution?
- Are recommendations missing risk or rollback notes?

If gaps remain:
1. Run targeted re-queries.
2. Update findings and recommendations.
3. Publish with a clear "Research Gaps" section if uncertainty remains.

## Citation Rules
- Use numbered citations in-line: [1], [2], [3].
- Keep a source list at the end with full URL and date.
- Prioritize primary sources for key claims.
- If citing secondary sources, cross-check with at least one independent source.

## Quality Bar
Deliver only when all are true:
- Sub-questions are fully covered.
- Evidence quality thresholds are met, or exceptions are explained.
- Output provides a clear decision path, not only a summary.
- Tradeoffs and risks are explicit.
- Sources are transparent and verifiable.
