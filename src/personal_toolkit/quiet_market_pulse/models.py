from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


SourceName = Literal["binance", "twse"]


@dataclass(frozen=True)
class InstrumentConfig:
    label: str
    symbol: str
    source: SourceName
    show_when_closed: bool = False


@dataclass(frozen=True)
class PulseConfig:
    refresh_seconds: int
    instruments: tuple[InstrumentConfig, ...]


@dataclass(frozen=True)
class Quote:
    label: str
    symbol: str
    price: float
    change_percent: float | None
    market_state: str | None = None
