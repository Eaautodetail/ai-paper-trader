# Weekly strategy review

* Date: 2026-10-31; history: 21 trading days of real 1-minute data (14 older days used for ranking, 7 recent days for checking)
* Strategy before the review: `{"name": "momentum_leaders", "params": {"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 4.0, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75}}`
* Decision: **No candidate beat the current strategy clearly enough on both older and recent days; keeping it.**
* Strategy from now on: `{"name": "momentum_leaders", "params": {"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 4.0, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75}}`

Top candidates (net USD after all costs, starting from 500 SEK each time):

| Strategy | Params | Older days: trades / net | Recent days: trades / net | Move before costs | Costs |
|---|---|---|---|---|---|
| orb | `{"or_minutes": 5, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 2 / +0.26 | 0 / +0.00 | +0.33 | 0.07 |
| orb | `{"or_minutes": 30, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 2 / +0.34 | 1 / -0.12 | +0.35 | 0.13 |
| orb | `{"or_minutes": 30, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 2 / +0.34 | 1 / -0.12 | +0.35 | 0.13 |
| orb | `{"or_minutes": 5, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 5 / +0.57 | 3 / -0.36 | +0.52 | 0.31 |
| orb | `{"or_minutes": 30, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 1 / +0.15 | 0 / +0.00 | +0.19 | 0.04 |
| orb | `{"or_minutes": 30, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 1 / +0.15 | 0 / +0.00 | +0.19 | 0.04 |
| momentum_leaders | `{"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 4.0, "take_profit": 0.08, "first_minute": 15, "last_entry_minute": 75, "market_filter": true}` | 12 / +0.59 | 9 / -0.52 | +0.95 | 0.87 |
| no_trade | `{}` | 0 / +0.00 | 0 / +0.00 | +0.00 | 0.00 |
| orb | `{"or_minutes": 15, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 2 / +0.09 | 1 / -0.15 | +0.06 | 0.13 |
| orb | `{"or_minutes": 15, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 4 / +0.16 | 2 / -0.27 | +0.14 | 0.25 |
| momentum_leaders | `{"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 4.0, "take_profit": 0.08, "first_minute": 15, "last_entry_minute": 75}` | 15 / +0.35 | 11 / -0.51 | +0.94 | 1.10 |
| momentum_leaders | `{"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 4.0, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75, "market_filter": true}` | 13 / +0.28 | 9 / -0.52 | +0.64 | 0.87 |

_Past results do not guarantee future results. The review can only pick among fixed, tested strategies._
