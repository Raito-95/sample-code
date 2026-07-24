from personal_toolkit.quiet_market_pulse.config import DEFAULT_CONFIG_PATH, load_config, parse_config


def test_parse_config_accepts_watchlist() -> None:
    config = parse_config(
        {
            "refresh_seconds": 60,
            "instruments": [
                {
                    "label": "BTC",
                    "symbol": "BTCUSDT",
                    "source": "binance",
                    "show_when_closed": True,
                }
            ],
        }
    )

    assert config.refresh_seconds == 60
    assert config.instruments[0].label == "BTC"
    assert config.instruments[0].show_when_closed is True


def test_parse_config_accepts_twse_source() -> None:
    config = parse_config(
        {
            "refresh_seconds": 60,
            "instruments": [{"label": "TWII", "symbol": "^TWII", "source": "twse"}],
        }
    )

    assert config.instruments[0].source == "twse"


def test_parse_config_rejects_too_fast_refresh() -> None:
    try:
        parse_config({"refresh_seconds": 1, "instruments": [{"label": "BTC", "symbol": "BTCUSDT", "source": "binance"}]})
    except ValueError as exc:
        assert "refresh_seconds" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_parse_config_rejects_string_boolean() -> None:
    try:
        parse_config(
            {
                "refresh_seconds": 60,
                "instruments": [
                    {
                        "label": "BTC",
                        "symbol": "BTCUSDT",
                        "source": "binance",
                        "show_when_closed": "false",
                    }
                ],
            }
        )
    except ValueError as exc:
        assert "show_when_closed" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_default_config_does_not_depend_on_working_directory(
    monkeypatch,
) -> None:
    monkeypatch.chdir(DEFAULT_CONFIG_PATH.parent)

    config = load_config()

    assert DEFAULT_CONFIG_PATH.is_absolute()
    assert [instrument.label for instrument in config.instruments] == ["TWII", "BTC", "ETH"]


def test_parse_config_rejects_non_integer_refresh() -> None:
    for value in (True, "60", 60.5):
        try:
            parse_config(
                {
                    "refresh_seconds": value,
                    "instruments": [{"label": "BTC", "symbol": "BTCUSDT", "source": "binance"}],
                }
            )
        except ValueError as exc:
            assert "refresh_seconds" in str(exc)
        else:
            raise AssertionError(f"expected ValueError for {value!r}")


def test_parse_config_rejects_duplicate_instruments() -> None:
    try:
        parse_config(
            {
                "instruments": [
                    {"label": "BTC", "symbol": "BTCUSDT", "source": "binance"},
                    {"label": "Bitcoin", "symbol": "btcusdt", "source": "binance"},
                ]
            }
        )
    except ValueError as exc:
        assert "duplicate instrument" in str(exc)
    else:
        raise AssertionError("expected ValueError")
