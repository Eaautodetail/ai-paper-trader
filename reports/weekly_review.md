# Weekly strategy review

* Date: 2026-11-07; history: 21 trading days of real 1-minute data (14 older days used for ranking, 7 recent days for checking)
* Strategy before the review: `{"name": "momentum_leaders", "params": {"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 4.0, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75}}`
* Decision: **Switching: orb beat the current strategy by +0.80 USD over all tested days and also on the most recent days.**
* Strategy from now on: `{"name": "orb", "params": {"or_minutes": 5, "rvol_min": 2.0, "target_r": 2.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}}`

Top candidates (net USD after all costs, starting from 500 SEK each time):

| Strategy | Params | Older days: trades / net | Recent days: trades / net | Move before costs | Costs |
|---|---|---|---|---|---|
| orb | `{"or_minutes": 5, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 6 / +0.21 | 3 / +0.20 | +0.76 | 0.35 |
| orb | `{"or_minutes": 30, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 2 / +0.34 | 2 / -0.07 | +0.43 | 0.17 |
| orb | `{"or_minutes": 30, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 2 / +0.34 | 2 / -0.07 | +0.43 | 0.17 |
| orb | `{"or_minutes": 5, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 1 / +0.15 | 2 / +0.07 | +0.33 | 0.12 |
| orb | `{"or_minutes": 5, "rvol_min": 2.0, "target_r": 2.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 14 / +0.10 | 9 / +0.07 | +1.22 | 1.04 |
| orb | `{"or_minutes": 15, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 3 / -0.12 | 6 / +0.29 | +0.52 | 0.35 |
| orb | `{"or_minutes": 30, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 1 / +0.15 | 2 / -0.07 | +0.20 | 0.12 |
| orb | `{"or_minutes": 30, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 1 / +0.15 | 2 / -0.07 | +0.20 | 0.12 |
| no_trade | `{}` | 0 / +0.00 | 0 / +0.00 | +0.00 | 0.00 |
| orb | `{"or_minutes": 15, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 5 / -0.44 | 6 / +0.29 | +0.30 | 0.45 |
| orb | `{"or_minutes": 15, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 3 / -0.06 | 3 / -0.13 | +0.07 | 0.26 |
| orb | `{"or_minutes": 30, "rvol_min": 2.0, "target_r": 2.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 11 / -0.21 | 7 / +0.01 | +0.62 | 0.83 |

_Past results do not guarantee future results. The review can only pick among fixed, tested strategies._
