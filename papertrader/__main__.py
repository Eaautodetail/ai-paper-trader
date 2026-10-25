"""Command line: python -m papertrader <command>

  run-session   run today's session if one is due (used by the schedule)
  check-data    verify Yahoo data, USD/SEK and the exchange calendar right now
  backtest      compare candidate strategies on recent 1-minute data
  status        rewrite STATUS.md
  start | stop | rehearse DATE   change control/state.json (used by the Control workflow)
"""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from . import control
from .config import ROOT, load_config
from .live import Runtime, SessionSkipped, YahooFeed, run_once, write_status
from .market_calendar import MarketCalendar


def git_persist(msg: str) -> None:
    """Commit the ledger, reports and status to GitHub (only inside GitHub Actions)."""
    if os.environ.get("PAPERTRADER_GIT_PERSIST") != "1":
        return
    paths = ["ledger", "reports", "STATUS.md", "data"]
    try:
        subprocess.run(["git", "add", *paths], cwd=ROOT, check=True)
        if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode == 0:
            return
        subprocess.run(["git", "commit", "-q", "-m", f"paper-trading: {msg} [skip ci]"], cwd=ROOT, check=True)
        for _ in range(4):
            # Only this job writes the ledger and reports; if the Control workflow changed
            # STATUS.md at the same moment, keep this job's (newer) version.
            if subprocess.run(["git", "pull", "-q", "--rebase", "-X", "theirs", "origin", "main"], cwd=ROOT).returncode != 0:
                subprocess.run(["git", "rebase", "--abort"], cwd=ROOT, capture_output=True)
                continue
            if subprocess.run(["git", "push", "-q", "origin", "HEAD:main"], cwd=ROOT).returncode == 0:
                return
        print("WARNING: could not push ledger update; will retry on next change", flush=True)
    except Exception as e:
        print(f"WARNING: persist failed: {e}", flush=True)


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    cmd = argv[0] if argv else "status"
    cfg = load_config()
    cal = MarketCalendar(cfg)
    in_actions = os.environ.get("PAPERTRADER_GIT_PERSIST") == "1"
    rt = Runtime(ROOT, cfg, YahooFeed(cfg, cal.tz), now=lambda: datetime.now(cal.tz),
                 control=(lambda: control.read_remote(ROOT)) if in_actions else None, persist=git_persist)

    if cmd == "run-session":
        try:
            msg = run_once(rt)
        except SessionSkipped as e:
            print(f"Session skipped safely: {e}")
            return 3
        print(msg)
        write_status(rt, cal, msg)
        git_persist("status")
        return 0
    if cmd == "check-data":
        from .live import data_is_current
        from . import data as md
        now = datetime.now(cal.tz)
        w = cal.window(now.date())
        print(f"Now: {now:%Y-%m-%d %H:%M} New York; trading day: {w is not None}")
        nxt = cal.next_window(now)
        print(f"Next window: {nxt.start:%Y-%m-%d %H:%M}-{nxt.end:%H:%M} New York = {nxt.display(cal.display_tz)}"
              f"{' (early close)' if nxt.early_close else ''}")
        fx = md.usdsek(cfg["universe"]["fx_symbol"])
        print(f"USD/SEK: {fx:.4f} -> 500 SEK = {500 * (1 - cfg['capital']['fx_conversion_fee_pct'] / 100) / fx:.2f} USD")
        d = md.daily(cfg["universe"]["symbols"], cal.tz)
        print(f"Daily bars: {len(d)}/{len(cfg['universe']['symbols'])} symbols")
        bench = cfg["universe"]["benchmark"]
        bars = md.download([bench], cal.tz, period="5d", interval="1m").get(bench)
        print(f"1-minute {bench} bars (last 5 days): {0 if bars is None else len(bars)}; newest {None if bars is None else bars.index[-1]}")
        if w and w.open <= now <= w.close:
            print("Live check:", data_is_current(rt, cal.tz, w, now))
        return 0 if bars is not None and len(bars) else 1
    if cmd == "backtest":
        from .backtest import run
        sel = run(cfg, ROOT / "reports", root=ROOT)
        (ROOT / "strategy").mkdir(exist_ok=True)
        (ROOT / "strategy" / "selected.json").write_text(json.dumps(sel, indent=2) + "\n")
        print(json.dumps(sel, indent=2))
        return 0
    if cmd == "backtest-momentum":
        # Compare the momentum strategy with the current one without changing strategy/selected.json.
        from .backtest import run
        from .strategies import build, momentum_grid
        current = json.loads((ROOT / "strategy" / "selected.json").read_text())["strategy"]
        sel = run(cfg, ROOT / "reports", strategies=[build({"name": "no_trade"}), build(current)] + momentum_grid(),
                  tag="backtest_momentum", root=ROOT)
        print(json.dumps(sel, indent=2))
        return 0
    if cmd == "fullday-study":
        # Research only: compares later daily deadlines; does not change the schedule or strategy.
        from .fullday import study
        res = study(cfg, ROOT)
        print(json.dumps(res["real_trades"], indent=2))
        for r in res["backtest"]:
            print(r)
        return 0
    if cmd == "set-evaluation-strategy":
        from .ledger import Ledger
        from .strategies import build
        spec = json.loads(argv[1])
        build(spec)  # must be a known strategy with valid parameters
        led = Ledger(ROOT / "ledger" / "evaluation.sqlite")
        led.set_strategy(spec, argv[2] if len(argv) > 2 else "changed by the user")
        led.close()
        return 0
    if cmd == "weekly-review":
        from .review import weekly_review
        print(json.dumps(weekly_review(cfg, ROOT), indent=2, default=str))
        write_status(rt, cal)
        return 0
    if cmd == "status":
        write_status(rt, cal)
        print((ROOT / "STATUS.md").read_text())
        return 0
    if cmd == "start":
        print(control.write(ROOT, evaluation_enabled=True, stop_requested=False))
        return 0
    if cmd == "stop":
        print(control.write(ROOT, stop_requested=True))
        return 0
    if cmd == "rehearse":
        print(control.write(ROOT, rehearsal_date=argv[1]))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
