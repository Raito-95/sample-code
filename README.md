# Workday Toolkit

This repository contains small, focused tools for recurring workday tasks.

It is not a generic Python sample-code collection, a teaching notebook, or a place to collect unrelated app ideas. The goal is to keep useful, narrowly scoped utilities that address specific workflow gaps.

## Current Tool

The first active tool is **Quiet Market Pulse**.

Quiet Market Pulse is a small, always-on market pulse UI. It sits at the bottom-right of the screen and shows watched symbols, price, and percent change.

- Taiwan Weighted Index
- BTC
- ETH

The Taiwan index only shows while its market is open. BTC and ETH stay visible.

## Principles

- Start from repeated real friction, not from generic tool ideas.
- Prefer mature software unless it misses a specific workflow need.
- Keep the repo small.
- Document decisions before adding implementation.
- Delete experiments that do not become useful.

## Layout

- `src/personal_toolkit/quiet_market_pulse/`: active market pulse tool
- `config/quiet-market-pulse.example.json`: default watchlist
- `start_quiet_market_pulse.py`: direct UI launcher
- `docs/quiet-market-pulse-plan.md`: tool plan and scope
- `docs/decisions/001-project-direction.md`: project direction decision
- `tests/`: focused tests

## Run

```bash
.\.venv\Scripts\python.exe start_quiet_market_pulse.py
```

Debug summary:

```bash
uv run quiet-market-pulse
```

## Current Check

```bash
uv run --group dev ruff check .
uv run --group dev pytest tests/
```
