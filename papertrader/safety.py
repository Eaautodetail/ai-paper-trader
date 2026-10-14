"""Hard safety switches. Real-money trading does not exist in this codebase.

There is no brokerage client, no order API and no account credential anywhere in the
project. These checks make that explicit and make the program refuse to run if anyone
tries to flip the mode.
"""

LIVE_TRADING_ENABLED = False  # Constant. Not read from config, environment or files.


class SafetyError(RuntimeError):
    pass


def assert_paper_only(cfg: dict) -> None:
    if LIVE_TRADING_ENABLED is not False:
        raise SafetyError("Live trading flag is set; refusing to run.")
    if cfg.get("mode", {}).get("paper_trading") is not True:
        raise SafetyError("config.toml must have [mode] paper_trading = true; refusing to run.")
    for key in ("live", "broker_api_key", "broker_url"):
        if key in cfg.get("mode", {}):
            raise SafetyError(f"Unsupported setting [mode] {key}; real trading is not part of this project.")
