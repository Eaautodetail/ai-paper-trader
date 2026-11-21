# Weekly strategy review

* Date: 2026-11-21; history: 25 trading days of real 1-minute data (17 older days used for ranking, 8 recent days for checking)
* Strategy before the review: `{"name": "orb", "params": {"or_minutes": 5, "rvol_min": 2.0, "target_r": 2.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}}`
* Decision: **Switching: orb beat the current strategy by +0.27 USD over all tested days and also on the most recent days.**
* Strategy from now on: `{"name": "orb", "params": {"or_minutes": 5, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}}`

Top candidates (net USD after all costs, starting from 500 SEK each time):

| Strategy | Params | Older days: trades / net | Recent days: trades / net | Move before costs | Costs |
|---|---|---|---|---|---|
| no_trade | `{}` | 0 / +0.00 | 0 / +0.00 | +0.00 | 0.00 |
| orb | `{"or_minutes": 5, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 7 / -0.19 | 3 / +0.14 | +0.32 | 0.38 |
| orb | `{"or_minutes": 5, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 11 / -0.16 | 10 / +0.02 | +0.62 | 0.76 |
| orb | `{"or_minutes": 5, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 5 / -0.26 | 2 / +0.01 | +0.03 | 0.27 |
| orb | `{"or_minutes": 30, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 6 / -0.12 | 3 / -0.17 | +0.05 | 0.34 |
| orb | `{"or_minutes": 30, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 6 / -0.12 | 3 / -0.17 | +0.05 | 0.34 |
| orb | `{"or_minutes": 15, "rvol_min": 2.0, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 7 / -0.07 | 4 / -0.30 | +0.07 | 0.44 |
| orb | `{"or_minutes": 5, "rvol_min": 2.0, "target_r": 2.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 21 / -0.41 | 3 / +0.00 | +0.63 | 1.03 |
| orb | `{"or_minutes": 5, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 9 / -0.22 | 8 / -0.22 | +0.18 | 0.62 |
| orb | `{"or_minutes": 30, "rvol_min": 2.0, "target_r": 2.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 18 / -0.31 | 4 / -0.19 | +0.46 | 0.95 |
| orb | `{"or_minutes": 15, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 10 / +0.35 | 8 / -0.86 | +0.19 | 0.70 |
| orb | `{"or_minutes": 30, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 7 / -0.27 | 5 / -0.43 | -0.25 | 0.45 |

_Past results do not guarantee future results. The review can only pick among fixed, tested strategies._
