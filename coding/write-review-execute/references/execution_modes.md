# Execution Modes

Pick execution mode before recommending a winner.

## Mode Question

Ask this question once near the start:

`Choose execution mode for this comparison: theoretical-only or proof-of-concept?`

## Mode Definitions

- `theoretical-only`
  - Do not run commands.
  - Rank alternatives using static review only.
  - Mark recommendation confidence as reduced because behavior was not executed.

- `proof-of-concept`
  - Run a minimal command set per scaffold to validate core behavior.
  - Capture command, short output summary, and pass or fail signal.
  - Prefer representative checks over full production test suites when speed matters.

## Fallback Rule

If the user does not answer the mode question:

1. Use `proof-of-concept` if a runnable command exists.
2. Use `theoretical-only` if no runnable command exists.

Always state when fallback was used.

## Confidence Guidance

- Highest confidence: all three scaffolds executed with clear pass or fail evidence.
- Medium confidence: partial execution coverage or weak command relevance.
- Reduced confidence: theoretical-only ranking with no execution evidence.
