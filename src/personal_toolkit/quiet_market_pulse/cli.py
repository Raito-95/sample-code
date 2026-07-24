from __future__ import annotations

from personal_toolkit.quiet_market_pulse.config import DEFAULT_CONFIG_PATH, load_config
from personal_toolkit.quiet_market_pulse.formatting import compact_summary
from personal_toolkit.quiet_market_pulse.pulse import collect_visible_quotes


def main() -> int:
    config = load_config(DEFAULT_CONFIG_PATH)
    print(compact_summary(collect_visible_quotes(config)))
    return 0
