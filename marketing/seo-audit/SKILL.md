---
name: seo-audit
description: Diagnose SEO performance problems and produce an actionable technical and on-page remediation plan. Use when users ask for an SEO audit, ranking drop analysis, indexing or crawl debugging, Core Web Vitals review, or broad organic growth diagnostics for a site or set of pages.
---

# SEO Audit

Use this skill to run a structured SEO audit and return a prioritized fix plan.

## Workflow

1. Scope the audit.
- Capture site type, target market, priority pages, and business objective.
- Define scope: full site or selected templates/pages.
- Confirm available data sources (Search Console, analytics, crawler exports).

2. Build a baseline.
- Record current traffic, top landing pages, and rank trends if available.
- Capture known incidents (migration, redesign, tracking change, algorithm hit).
- Define success metrics for this audit cycle.

3. Check crawlability and indexation.
- Review `robots.txt`, XML sitemap quality, and canonical consistency.
- Identify blocked or orphaned money pages.
- Flag redirect chains, soft 404s, duplicate URL variants, and noindex mistakes.

4. Check technical foundations.
- Review page speed and Core Web Vitals risks by template.
- Verify mobile usability, HTTPS consistency, and URL hygiene.
- Note rendering or JavaScript dependency risks that hide content from crawlers.

5. Check on-page execution.
- Audit titles, meta descriptions, heading hierarchy, and primary intent match.
- Validate internal linking patterns and anchor relevance.
- Flag thin, duplicate, stale, or cannibalizing content.

6. Check authority and trust signals.
- Review backlink profile at high level if data is available.
- Flag obvious quality or relevance gaps in external signals.
- Recommend the smallest set of authority-building actions tied to key pages.

7. Prioritize the fix plan.
- Classify each issue by `severity` (`critical`, `high`, `medium`, `low`).
- Score each fix by impact, effort, and confidence.
- Sequence actions: unblock indexing first, then performance, then on-page improvements.

8. Deliver implementation guidance.
- Provide a 30/60/90-day action plan.
- Include owner suggestions (`engineering`, `content`, `marketing`).
- Define expected movement and how to validate each completed fix.

## Output Rules

- Separate facts, assumptions, and unknowns.
- Never claim schema absence from static fetch alone.
- Prefer specific fixes over generic best-practice advice.
- Always include validation checks for each recommended action.

## References

- [ai-writing-detection.md](references/ai-writing-detection.md)
