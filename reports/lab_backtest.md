# Strategy backtest

Real 1-minute Yahoo bars, same simulator, risk limits and costs as paper trading, starting from 500 SEK.
Only 09:30-11:30 New York time is traded. **This is a short sample and is not evidence of a profitable edge.**
If 'move before costs' is negative, the strategy lost before any fees, so a bigger trade size would only lose more.

* Data: 2026-09-30 to 2026-10-28; in-sample 14 days, out-of-sample 7 days
* USD/SEK used: 9.8375; starting cash 50.70 USD after conversion fee
* Selection rule: Highest in-sample net P&L after all modeled costs among variants with >= 5 in-sample trades; out-of-sample days are reported but not used for the choice.
* **Selected: `orb` {"or_minutes": 5, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}**
* Out-of-sample check passed: **no**

| Strategy | Params | IS trades | IS net USD | IS max DD % | OOS trades | OOS net USD | OOS win % | All days: move before costs USD | All days: costs USD | Most common rejections |
|---|---|---|---|---|---|---|---|---|---|---|
| orb | `{"or_minutes": 5, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 6 | 0.6461 | 0.0 | 2 | -0.2406 | 0.0 | +0.7078 | 0.3024 | market (59); expected gain 0.019 USD is under 2x costs 0.038 USD (3); expected gain 0.026 USD is under 2x costs 0.036 USD (3) |
| rules | `{"first_minute": 15, "last_entry_minute": 75, "stop_atr": 4.0, "trail": true, "target_r": null, "take_profit": 0.03, "score": "gain", "min_gain": 0.03, "rvol_min": 1.5, "new_high_minutes": 10, "above_vwap": true, "uptrend": true, "spy_min_gain": 0.003}` | 4 | 0.0072 | -0.148 | 5 | 0.4537 | 60.0 | +0.7924 | 0.3313 | already have a position or order in this symbol (10); max open positions reached (4); already traded this symbol this session (2) |
| no_trade | `{}` | 0 | 0.0 | 0.0 | 0 | 0.0 | - | +0.0000 | 0.0000 |  |
| rules | `{"first_minute": 20, "last_entry_minute": 100, "stop_atr": 4.0, "trail": false, "target_r": null, "take_profit": 0.015, "score": "dip", "min_gain": 0.0, "below_vwap_atr": 1.0, "rsi_max": 35, "spy_above_vwap": true}` | 1 | -0.0194 | -0.038 | 5 | -0.5517 | 0.0 | -0.3308 | 0.2402 | already have a position or order in this symbol (17); expected gain 0.060 USD is under 2x costs 0.036 USD (10); expected gain 0.059 USD is under 2x costs 0.036 USD (9) |
| rules | `{"first_minute": 15, "last_entry_minute": 75, "stop_atr": 4.0, "trail": true, "target_r": null, "take_profit": 0.03, "score": "gain", "min_gain": 0.03, "rvol_min": 1.5, "new_high_minutes": 10, "above_vwap": true, "uptrend": true, "min_price": 5.0, "max_vwap_atr": 3.0}` | 2 | -0.0275 | -0.054 | 2 | 0.0253 | 50.0 | +0.1496 | 0.1516 | planned loss for 1 share exceeds the per-trade limit (1) |
| rules | `{"first_minute": 45, "last_entry_minute": 90, "stop_atr": 4.0, "trail": true, "target_r": null, "take_profit": 0.03, "score": "gain", "min_gain": 0.03, "rvol_min": 1.5, "new_high_minutes": 10, "above_vwap": true, "uptrend": true}` | 12 | -0.3179 | -0.774 | 16 | -0.4262 | 37.5 | +0.3898 | 1.1339 | already have a position or order in this symbol (34); max open positions reached (10) |
| momentum_leaders | `{"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 4.0, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75}` | 14 | -0.4772 | -0.941 | 15 | -0.0003 | 40.0 | +0.6808 | 1.1584 | already have a position or order in this symbol (30); max open positions reached (11); already traded this symbol this session (2) |
