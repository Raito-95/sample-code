import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))


def _main() -> int:
    from personal_toolkit.quiet_market_pulse.tray import main

    return main()


if __name__ == "__main__":
    raise SystemExit(_main())
