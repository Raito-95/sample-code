# 001 Project Direction

## Context

The old repo mixed sample code, teaching notes, algorithms, data structures, and a few small desktop tools. That made the project hard to define and easy to overgrow.

The new repo should start from recurring practical workflows instead of generic programming practice. The first use case is a quiet market pulse tool for checking a small set of symbols during work without opening a full trading app.

## Decision

Define this repo as a **focused workday toolkit**.

The first active tool is **Quiet Market Pulse**.

## In Scope

- Daily-use workflow tools
- Small utilities that fit workday rhythm
- Configurable but not overly general workflows
- Clear docs before implementation
- Focused tests once behavior exists

## Out of Scope

- Generic Python sample code
- Teaching notes
- Full trading terminals
- News aggregation
- Portfolio/account tracking
- Social feeds
- Large dashboards
- Feature work without a clear daily use case

## Consequences

- New code should serve a concrete recurring workflow.
- The repo should stay small until a tool proves useful.
- Experiments can be deleted when they do not solve enough pain.
- If a future idea does not fit daily use, it belongs in notes, not code.
