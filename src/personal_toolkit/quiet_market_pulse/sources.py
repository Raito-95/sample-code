from __future__ import annotations

import json
import math
from dataclasses import replace
from http.client import HTTPException
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from personal_toolkit.quiet_market_pulse.models import InstrumentConfig, Quote


MAX_JSON_RESPONSE_BYTES = 1_000_000


class QuoteUnavailable(RuntimeError):
    """Raised when a quote cannot be fetched or parsed."""


def fetch_quote(instrument: InstrumentConfig, timeout: float = 8.0) -> Quote:
    try:
        if instrument.source == "binance":
            return fetch_binance_quote(instrument, timeout=timeout)
        if instrument.source == "twse":
            return fetch_twse_quote(instrument, timeout=timeout)
    except (
        HTTPError,
        HTTPException,
        URLError,
        TimeoutError,
        OSError,
        ValueError,
        KeyError,
        TypeError,
    ) as exc:
        raise QuoteUnavailable(str(exc)) from exc

    raise QuoteUnavailable(f"unsupported source: {instrument.source}")


def fetch_binance_quote(instrument: InstrumentConfig, timeout: float = 8.0) -> Quote:
    query = urlencode({"symbol": instrument.symbol})
    payload = _read_json(
        f"https://api.binance.com/api/v3/ticker/24hr?{query}",
        timeout,
        expected_host="api.binance.com",
    )
    return parse_binance_ticker_payload(instrument, payload)


def fetch_twse_quote(instrument: InstrumentConfig, timeout: float = 8.0) -> Quote:
    channel = _twse_channel(instrument.symbol)
    query = urlencode({"ex_ch": channel, "json": "1", "delay": "0"})
    payload = _read_json(
        f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?{query}",
        timeout,
        expected_host="mis.twse.com.tw",
    )
    quote = parse_twse_quote_payload(payload)
    return replace(quote, label=instrument.label, symbol=instrument.symbol)


def parse_binance_ticker_payload(instrument: InstrumentConfig, payload: dict[str, Any]) -> Quote:
    return Quote(
        label=instrument.label,
        symbol=instrument.symbol,
        price=_finite_float(payload["lastPrice"], "lastPrice", positive=True),
        change_percent=_finite_float(payload["priceChangePercent"], "priceChangePercent"),
        market_state="REGULAR",
    )


def parse_twse_quote_payload(payload: dict[str, Any]) -> Quote:
    if payload.get("rtcode") != "0000":
        raise ValueError(f"twse quote error: {payload.get('rtmessage')}")

    results = payload["msgArray"]
    if not results:
        raise ValueError("empty twse quote result")

    item = results[0]
    price = _finite_float(str(item["z"]).replace(",", ""), "price", positive=True)
    previous_close = _finite_float(
        str(item["y"]).replace(",", ""),
        "previous close",
        positive=True,
    )
    change_percent = None
    if previous_close:
        change_percent = ((price - previous_close) / previous_close) * 100

    return Quote(
        label=str(item.get("n") or item.get("ch") or ""),
        symbol=str(item.get("ch") or ""),
        price=price,
        change_percent=change_percent,
        market_state=_twse_market_state(payload, item),
    )


def _twse_channel(symbol: str) -> str:
    normalized = symbol.strip()
    normalized_upper = normalized.upper()
    normalized_lower = normalized.lower()
    if normalized_upper in {"^TWII", "TWII", "TAIEX"}:
        return "tse_t00.tw"
    if normalized_lower in {"t00", "t00.tw", "tse_t00.tw"}:
        return "tse_t00.tw"
    if normalized_lower.startswith(("tse_", "otc_")) and normalized_lower.endswith(".tw"):
        return normalized_lower
    if normalized.isdigit():
        return f"tse_{normalized}.tw"
    raise ValueError(f"unsupported twse symbol: {symbol}")


def _finite_float(value: Any, field_name: str, *, positive: bool = False) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{field_name} must be finite")
    if positive and number <= 0:
        raise ValueError(f"{field_name} must be positive")
    return number


def _twse_market_state(payload: dict[str, Any], item: dict[str, Any]) -> str:
    query_time = payload.get("queryTime")
    if not isinstance(query_time, dict):
        return "CLOSED"

    quote_date = str(item.get("d") or "")
    sys_date = str(query_time.get("sysDate") or "")
    sys_time = str(query_time.get("sysTime") or item.get("t") or item.get("%") or "")

    if quote_date != sys_date:
        return "CLOSED"
    if "09:00:00" <= sys_time <= "13:30:00":
        return "REGULAR"
    return "CLOSED"


def _read_json(url: str, timeout: float, *, expected_host: str) -> dict[str, Any]:
    parsed_url = urlparse(url)
    if parsed_url.scheme != "https" or parsed_url.hostname != expected_host:
        raise ValueError("unexpected quote endpoint")

    request = Request(url, headers={"User-Agent": "personal-toolkit/0.1"})
    with urlopen(request, timeout=timeout) as response:
        data = response.read(MAX_JSON_RESPONSE_BYTES + 1)
    if len(data) > MAX_JSON_RESPONSE_BYTES:
        raise ValueError("response is too large")

    text = data.decode("utf-8")
    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise ValueError("response must be a JSON object")
    return payload
