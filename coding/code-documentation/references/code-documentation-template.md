# Code Documentation Template

Use the smallest variant that fits the request. Delete sections that do not add value.

## Repository Or Feature Document

```markdown
# [Name]

Short statement of what this code does and when to use it.

## Why It Exists

- Problem it solves
- Scope boundaries

## Entry Points

- Main files or modules
- Commands, routes, jobs, or exported APIs

## How It Works

1. Step or flow
2. Important branching behavior
3. Outputs or side effects

## Inputs And Configuration

| Name | Type | Required | Default | Notes |
|------|------|----------|---------|-------|

## Failure Modes

- Expected errors
- Retries, rollbacks, or recovery notes

## Validation

- How to run or test it
- Signals that confirm correct behavior

## Related Files

- `path/to/file`
- `path/to/other-file`
```

## Module Or File Document

```markdown
# [Module Name]

One-paragraph summary of responsibility and boundaries.

## Responsibilities

- Primary responsibility
- Explicit non-goals

## Key Exports Or Entry Points

- `symbolName`: what it is for

## Data Flow

1. Input source
2. Processing step
3. Output destination

## Edge Cases

- Non-obvious behavior
- Important constraints

## Change Notes

- What must stay true if this file is modified
```

## Function Or Method Docstring

```text
Purpose: what the function guarantees.
Inputs: required parameters and important assumptions.
Returns: value and meaning.
Side effects: I/O, mutation, logging, network, cache, events.
Failure cases: expected errors or invalid states.
```

## Review Prompts

- Can a new maintainer find the entry point in under 30 seconds?
- Does the doc explain constraints and failure behavior, not just happy path behavior?
- Are names, paths, commands, and interfaces aligned with the current code?
- Would this still be useful after the next refactor?
