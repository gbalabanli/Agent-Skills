# Clarifying Question Bank

Use these questions to resolve ambiguity quickly. Ask only what materially changes the outcome.

## Prompt Mode and Model

- Which task type best matches this request: coding, reasoning, extraction, research, or general?
- Which model family should this prompt target: GPT, reasoning model, or Codex?
- Do you want strict structured output (XML/JSON sections) or plain prose?

## Goal

- What is the exact end result you want the model to produce?
- If the model succeeds perfectly, what will be true at the end?
- What single outcome should be prioritized above everything else?

## Scope

- What is explicitly in scope for this request?
- What is explicitly out of scope?
- Should the model provide only a plan, only code, or both?

## Hard Constraints

- What constraints are non-negotiable (platform, language, security, deadlines, dependencies)?
- Are there forbidden tools, frameworks, or patterns?
- Are there performance or resource limits that must not be exceeded?
- Are there policies or safety rules the model must always follow?

## Optimization Constraints

- What should be optimized first: correctness, speed, cost, maintainability, or delivery time?
- How should tradeoffs be handled when optimization goals conflict?
- What is the preferred ranking of optimization priorities?

## Inputs and Context

- Which files, URLs, APIs, or examples must be used?
- What existing system context should the model assume?
- Are there reference implementations or style guides to follow?

## Output Contract

- What output format do you want (checklist, patch, markdown report, JSON, code)?
- Which sections are required in the final response?
- Should the response include alternatives or only one recommended path?
- Should the output be machine-parseable (strict XML/JSON schema)?

## Success Criteria

- How will you verify the result is correct?
- What acceptance checks must pass?
- What would make you reject the output as low quality?

## Verification Expectations

- Should the prompt require tests, lint, type checks, or sanity checks?
- Should sources/citations be required for factual claims?
- Should the model report commands/checks performed or just final results?

## Risk and Failure Boundaries

- What common failure mode must be avoided?
- What level of uncertainty is acceptable?
- Should the model ask follow-up questions instead of assuming when uncertain?
