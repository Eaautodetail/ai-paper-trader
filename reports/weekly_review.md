# Weekly strategy review

* Date: 2026-10-25; history: 21 trading days of real 1-minute data (14 older days used for ranking, 7 recent days for checking)
* Strategy before the review: `{"name": "momentum_leaders", "params": {"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 4.0, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75}}`
* Decision: **The current strategy is still the best tested one; keeping it.**
* Strategy from now on: `{"name": "momentum_leaders", "params": {"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 4.0, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75}}`

Top candidates (net USD after all costs, starting from 500 SEK each time):

| Strategy | Params | Older days: trades / net | Recent days: trades / net | Move before costs | Costs |
|---|---|---|---|---|---|
| momentum_leaders | `{"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 4.0, "take_profit": 0.08, "first_minute": 15, "last_entry_minute": 75, "market_filter": true}` | 8 / -0.38 | 8 / +0.91 | +1.19 | 0.65 |
| momentum_leaders | `{"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 4.0, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75, "market_filter": true}` | 8 / -0.38 | 9 / +0.70 | +0.96 | 0.64 |
| orb | `{"or_minutes": 5, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 3 / +0.19 | 2 / +0.02 | +0.40 | 0.19 |
| orb | `{"or_minutes": 30, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 0 / +0.00 | 1 / +0.15 | +0.19 | 0.04 |
| orb | `{"or_minutes": 30, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 0 / +0.00 | 1 / +0.15 | +0.19 | 0.04 |
| orb | `{"or_minutes": 5, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 0 / +0.00 | 1 / +0.15 | +0.19 | 0.04 |
| orb | `{"or_minutes": 30, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 0 / +0.00 | 1 / +0.15 | +0.19 | 0.04 |
| orb | `{"or_minutes": 30, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 0 / +0.00 | 1 / +0.15 | +0.19 | 0.04 |
| no_trade | `{}` | 0 / +0.00 | 0 / +0.00 | +0.00 | 0.00 |
| orb | `{"or_minutes": 15, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 0 / +0.00 | 2 / -0.00 | +0.07 | 0.08 |
| momentum_leaders | `{"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 2.0, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75, "market_filter": true}` | 8 / -0.34 | 9 / +0.29 | +0.63 | 0.68 |
| orb | `{"or_minutes": 5, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 0 / +0.00 | 2 / -0.06 | +0.05 | 0.11 |

_Past results do not guarantee future results. The review can only pick among fixed, tested strategies._
