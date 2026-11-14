# Weekly strategy review

* Date: 2026-11-14; history: 21 trading days of real 1-minute data (14 older days used for ranking, 7 recent days for checking)
* Strategy before the review: `{"name": "orb", "params": {"or_minutes": 5, "rvol_min": 2.0, "target_r": 2.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}}`
* Decision: **No candidate beat the current strategy clearly enough on both older and recent days; keeping it.**
* Strategy from now on: `{"name": "orb", "params": {"or_minutes": 5, "rvol_min": 2.0, "target_r": 2.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}}`

Top candidates (net USD after all costs, starting from 500 SEK each time):

| Strategy | Params | Older days: trades / net | Recent days: trades / net | Move before costs | Costs |
|---|---|---|---|---|---|
| orb | `{"or_minutes": 30, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 1 / +0.09 | 5 / +0.26 | +0.54 | 0.20 |
| orb | `{"or_minutes": 30, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 1 / +0.09 | 6 / +0.11 | +0.44 | 0.24 |
| orb | `{"or_minutes": 5, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 5 / -0.01 | 8 / +0.12 | +0.57 | 0.46 |
| orb | `{"or_minutes": 30, "rvol_min": 2.0, "target_r": 2.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 13 / -0.33 | 7 / +0.37 | +0.91 | 0.86 |
| orb | `{"or_minutes": 5, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 1 / +0.22 | 4 / -0.18 | +0.23 | 0.19 |
| orb | `{"or_minutes": 15, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 6 / -0.02 | 4 / +0.05 | +0.41 | 0.38 |
| no_trade | `{}` | 0 / +0.00 | 0 / +0.00 | +0.00 | 0.00 |
| orb | `{"or_minutes": 30, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 2 / -0.03 | 7 / +0.00 | +0.28 | 0.31 |
| orb | `{"or_minutes": 5, "rvol_min": 2.0, "target_r": 2.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 14 / +0.01 | 9 / -0.07 | +0.91 | 0.98 |
| orb | `{"or_minutes": 15, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 7 / -0.23 | 6 / +0.15 | +0.45 | 0.53 |
| orb | `{"or_minutes": 15, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 2 / -0.32 | 3 / +0.16 | +0.03 | 0.20 |
| orb | `{"or_minutes": 30, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 2 / -0.03 | 8 / -0.15 | +0.17 | 0.35 |

_Past results do not guarantee future results. The review can only pick among fixed, tested strategies._
