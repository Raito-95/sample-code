# Quiet Market Pulse Plan

## Purpose

Quiet Market Pulse is a small workday UI for checking a limited set of market signals.

It is not a trading terminal, a charting app, a portfolio tracker, or a news reader.

## Watchlist

- Taiwan Weighted Index
- BTC
- ETH

## Display Rules

- Show price.
- Show percent change.
- Do not show time.
- Do not show a title or header.
- Show the Taiwan index only while its market is open.
- Keep crypto symbols visible.
- Keep the UI small, stable, and suitable for staying open for a long time.

## UI

- Floating always-on-top window.
- Start at the bottom-right of the primary screen.
- Use one compact row per symbol.
- Align prices and percent changes for quick scanning.
- Use color only for percent change direction.
- Allow dragging if the default position is inconvenient.
- System tray menu:
  - Show/Hide
  - Exit
- No command prompt should be needed for normal use.
- Launch through `start_quiet_market_pulse.py`.

## Out of Scope

- Charts
- News
- Account login
- Trading
- Watchlist editing UI
- Alerts
- Historical analysis
