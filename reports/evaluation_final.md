# Evaluation report (3 paper-trading sessions)

_Simulated paper trading only. No real money, no brokerage connection. Results from a few sessions are an operational test, not evidence of a profitable strategy._

Paper trading now continues as training (see readiness.md). Live trading was never enabled and cannot be enabled by this program.

## Money

* Starting capital: 500.00 SEK -> 50.0868 USD (USD/SEK 9.9577, conversion fee 1.25 SEK)
* Final equity: 49.6395 USD = 490.81 SEK at USD/SEK 9.8874
* Trading result: -0.4473 USD (-0.893%) after all modeled costs
* Result in SEK incl. the conversion fee and currency moves: -9.19 SEK
* Modeled transaction costs (spread, slippage, fees): 0.1823 USD

## Activity

* Sessions: 2026-10-15 (completed), 2026-10-16 (completed), 2026-10-19 (completed)
* Round trips: 4; winners 0; losers 4
* Exits: window_end 1, stop 3
* Net P&L from trades: -0.4473 USD

## Session results

| Session | Status | Start USD | End USD | P&L USD | Trades |
|---|---|---|---|---|---|
| [2026-10-15](evaluation/2026-10-15.md) | completed | 50.0868 | 50.0388 | -0.0480 | 1 |
| [2026-10-16](evaluation/2026-10-16.md) | completed | 50.0388 | 49.8345 | -0.2043 | 1 |
| [2026-10-19](evaluation/2026-10-19.md) | completed | 49.8345 | 49.6395 | -0.1950 | 2 |

## Strategy

* 2026-10-15: `{'name': 'orb', 'params': {'or_minutes': 5, 'rvol_min': 2.0, 'target_r': 2.5, 'stop_atr': 2.0, 'last_entry_minute': 90}}`
* 2026-10-16: `{'name': 'orb', 'params': {'or_minutes': 5, 'rvol_min': 2.0, 'target_r': 2.5, 'stop_atr': 2.0, 'last_entry_minute': 90}}`
* 2026-10-19: `{'name': 'orb', 'params': {'or_minutes': 5, 'rvol_min': 2.0, 'target_r': 2.5, 'stop_atr': 2.0, 'last_entry_minute': 90}}`
* Strategy changed to {"name": "momentum_leaders", "params": {"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 2.0, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75}}: Albin asked for a strategy that buys stocks rising during the window; best in-sample momentum variant (reports/backtest_momentum.md)
* Strategy changed to {"name": "orb", "params": {"or_minutes": 5, "rvol_min": 2.0, "target_r": 2.5, "stop_atr": 2.0, "last_entry_minute": 90}}: Albin chose to keep the original strategy for the final session
* Chosen by backtest on 2026-09-15..2026-10-13; passed out-of-sample check: no (see backtest.md)

## Was it the fees?

Each trade's result split into the price move (before any costs) and the costs. Costs come in two kinds: *fixed* (US fees rounded up to whole cents, about 0.02 USD per sale no matter the size) and *proportional* (spread and slippage, a percentage of the trade). Fixed fees shrink in % as trades get bigger; proportional costs do not. This is analysis only: the real limits (20% of equity per position) are never raised.

| Stock | Trade size USD | Price move before costs | Costs | Net | Verdict |
|---|---|---|---|---|---|
| MARA | 8.03 | -0.0100 USD (-0.12%) | 0.0380 USD (0.47%) | -0.0480 USD | the price moved against us; no trade size would have made this a profit |
| OPEN | 9.51 | -0.1349 USD (-1.42%) | 0.0694 USD (0.73%) | -0.2043 USD | the price moved against us; no trade size would have made this a profit |
| BTG | 5.32 | -0.0559 USD (-1.05%) | 0.0353 USD (0.66%) | -0.0912 USD | the price moved against us; no trade size would have made this a profit |
| ITUB | 9.61 | -0.0643 USD (-0.67%) | 0.0396 USD (0.41%) | -0.1039 USD | the price moved against us; no trade size would have made this a profit |

Total price move before costs: -0.2650 USD; total costs: 0.1823 USD. 0 of 4 losing trades lost only because of fees; the rest would have lost at any size.

## How to read this

* Three sessions are far too few to judge profitability; the goal was to prove the system runs safely and records everything.
* Check that every position was closed by 11:30 New York time (exit reason `window_end` or earlier) and that no limits were broken.
* With 500 SEK, one position may be at most 20% (about 100 SEK), so only cheaper stocks fit and fixed fees weigh heavily.
* Nothing switches to real money. Any next step is your decision.
