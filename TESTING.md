# Testing Guide

Run lint:

```bash
uv run --group dev ruff check .
```

Run tests:

```bash
uv run --group dev pytest tests/
```

Current test scope:

- Quiet Market Pulse config validation
- Price and percent formatting
- Market-open visibility rules
- Quote source parsing and failure fallback
- CLI summary output
