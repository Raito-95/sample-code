from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from personal_toolkit.quiet_market_pulse.models import InstrumentConfig, PulseConfig, SourceName


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "quiet-market-pulse.example.json"
VALID_SOURCES: set[SourceName] = {"binance", "twse"}
MAX_INSTRUMENTS = 20
MAX_LABEL_LENGTH = 32
MAX_SYMBOL_LENGTH = 64


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> PulseConfig:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return parse_config(payload)


def parse_config(payload: Any) -> PulseConfig:
    if not isinstance(payload, dict):
        raise ValueError("config must be an object")

    refresh_seconds = payload.get("refresh_seconds", 60)
    if type(refresh_seconds) is not int:
        raise ValueError("refresh_seconds must be an integer")
    if refresh_seconds < 15:
        raise ValueError("refresh_seconds must be at least 15")

    raw_instruments = payload.get("instruments")
    if not isinstance(raw_instruments, list) or not raw_instruments:
        raise ValueError("instruments must be a non-empty list")
    if len(raw_instruments) > MAX_INSTRUMENTS:
        raise ValueError(f"instruments must contain at most {MAX_INSTRUMENTS} items")

    instruments: list[InstrumentConfig] = []
    seen_instruments: set[tuple[SourceName, str]] = set()
    for item in raw_instruments:
        if not isinstance(item, dict):
            raise ValueError("instrument must be an object")

        label = str(item.get("label", "")).strip()
        symbol = str(item.get("symbol", "")).strip()
        source = _parse_source(item.get("source", ""))

        if not label or not symbol:
            raise ValueError("instrument label and symbol are required")
        if len(label) > MAX_LABEL_LENGTH:
            raise ValueError(f"instrument label must be at most {MAX_LABEL_LENGTH} characters")
        if len(symbol) > MAX_SYMBOL_LENGTH:
            raise ValueError(f"instrument symbol must be at most {MAX_SYMBOL_LENGTH} characters")

        instrument_key = (source, symbol.upper())
        if instrument_key in seen_instruments:
            raise ValueError(f"duplicate instrument: {symbol}")
        seen_instruments.add(instrument_key)

        instruments.append(
            InstrumentConfig(
                label=label,
                symbol=symbol,
                source=source,
                show_when_closed=_parse_bool(item.get("show_when_closed"), "show_when_closed"),
            )
        )

    return PulseConfig(refresh_seconds=refresh_seconds, instruments=tuple(instruments))


def _parse_source(value: Any) -> SourceName:
    source = str(value).strip()
    if source not in VALID_SOURCES:
        raise ValueError(f"unsupported source: {source}")
    return cast(SourceName, source)


def _parse_bool(value: Any, field_name: str) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    raise ValueError(f"{field_name} must be a boolean")
