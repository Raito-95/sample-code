# Contributing

## Current Intent

This repo is a focused workday toolkit.

Do not add generic sample code, teaching notes, or tools without a clear recurring workflow use case.

## Before Adding Code

Keep changes aligned with the active tool direction in `docs/quiet-market-pulse-plan.md`.

Capture new tool ideas in a short decision note before implementation:

- What situation keeps repeating?
- What is annoying, slow, distracting, or easy to forget?
- How often does it happen?
- What do you do today instead?
- Why is mature software not sufficient here?

Only add a decision file under `docs/decisions/` when the problem is worth implementing:

- What problem is this repo solving?
- Who is the tool for?
- What is explicitly out of scope?
- What is the smallest useful first version?

## Checks

Run lint before committing:

```bash
uv run --group dev ruff check .
uv run --group dev pytest tests/
```
