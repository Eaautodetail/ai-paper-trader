# Weekly strategy review

* Date: 2026-10-17; history: 21 trading days of real 1-minute data (14 older days used for ranking, 7 recent days for checking)
* Strategy before the review: `{"name": "orb", "params": {"or_minutes": 5, "rvol_min": 2.0, "target_r": 2.5, "stop_atr": 2.0, "last_entry_minute": 90}}`
* Decision: **The 3-session evaluation is still running; the strategy is not changed during it.**
* Strategy from now on: `{"name": "orb", "params": {"or_minutes": 5, "rvol_min": 2.0, "target_r": 2.5, "stop_atr": 2.0, "last_entry_minute": 90}}`

Top candidates (net USD after all costs, starting from 500 SEK each time):

| Strategy | Params | Older days: trades / net | Recent days: trades / net | Move before costs | Costs |
|---|---|---|---|---|---|
| orb | `{"or_minutes": 5, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 1 / +0.08 | 4 / +0.45 | +0.73 | 0.20 |
| orb | `{"or_minutes": 30, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 0 / +0.00 | 1 / +0.15 | +0.19 | 0.04 |
| orb | `{"or_minutes": 30, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 0 / +0.00 | 1 / +0.15 | +0.19 | 0.04 |
| orb | `{"or_minutes": 5, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 0 / +0.00 | 1 / +0.15 | +0.19 | 0.04 |
| orb | `{"or_minutes": 30, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 0 / +0.00 | 1 / +0.15 | +0.19 | 0.04 |
| orb | `{"or_minutes": 30, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 0 / +0.00 | 1 / +0.15 | +0.19 | 0.04 |
| orb | `{"or_minutes": 15, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 0 / +0.00 | 2 / +0.09 | +0.18 | 0.09 |
| orb | `{"or_minutes": 5, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 1 / +0.09 | 2 / -0.06 | +0.17 | 0.14 |
| orb | `{"or_minutes": 15, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 0 / +0.00 | 2 / +0.03 | +0.11 | 0.08 |
| no_trade | `{}` | 0 / +0.00 | 0 / +0.00 | +0.00 | 0.00 |
| orb | `{"or_minutes": 5, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 3 / +0.22 | 6 / -0.22 | +0.37 | 0.37 |
| orb | `{"or_minutes": 15, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 1 / +0.09 | 3 / -0.12 | +0.16 | 0.19 |

_Past results do not guarantee future results. The review can only pick among fixed, tested strategies._
