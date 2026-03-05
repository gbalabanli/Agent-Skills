---
name: analytics-tracking
description: Design or audit product and marketing analytics instrumentation for reliable decision-making. Use when users ask for event taxonomy, GA4 or GTM setup, funnel tracking, attribution instrumentation, analytics QA, or reporting models tied to growth goals.
---

# Analytics Tracking

Use this skill to turn business questions into reliable tracking implementation.

## Workflow

1. Define measurement scope.
- Capture product model, funnel stages, and target KPIs.
- Translate goals into measurable questions.
- Identify required attribution granularity and decision cadence.

2. Audit current tracking state.
- Inventory existing events, parameters, and destinations.
- Detect naming collisions, missing context, and duplicate events.
- Flag broken or ambiguous funnel steps.

3. Design event taxonomy.
- Standardize event naming and parameter conventions.
- Define required properties for user, session, context, and outcome.
- Separate behavioral events from system events.

4. Map events to decisions.
- Tie each event to one reporting use case.
- Define north-star events and guardrail metrics.
- Remove events with no clear decision value.

5. Specify implementation plan.
- Produce implementation details for product instrumentation, GTM, and GA4.
- Define trigger logic, parameter validation, and edge-case handling.
- Include identity model rules (anonymous, logged-in, merged users).

6. Define QA and governance.
- Create pre-launch and post-launch validation checklist.
- Define data quality monitors and alert thresholds.
- Set ownership and versioning rules for schema changes.

7. Deliver reporting starter pack.
- Provide core funnel and cohort views required by the scope.
- Include metric definitions and caveats.
- Recommend first weekly review agenda.

## Output Rules

- Express taxonomy as a table with event names, trigger, parameters, and owner.
- Distinguish required vs optional parameters.
- Do not recommend tracking that has no decision use.
- Call out privacy, consent, and compliance implications explicitly.

## References

- [event-library.md](references/event-library.md)
- [ga4-implementation.md](references/ga4-implementation.md)
- [gtm-implementation.md](references/gtm-implementation.md)
