# Strategy backtest

Real 1-minute Yahoo bars, same simulator, risk limits and costs as paper trading, starting from 500 SEK.
Only 09:30-11:30 New York time is traded. **This is a short sample and is not evidence of a profitable edge.**
If 'move before costs' is negative, the strategy lost before any fees, so a bigger trade size would only lose more.

* Data: 2026-10-02 to 2026-10-30; in-sample 14 days, out-of-sample 7 days
* USD/SEK used: 9.8133; starting cash 50.82 USD after conversion fee
* Selection rule: Highest in-sample net P&L after all modeled costs among variants with >= 5 in-sample trades; out-of-sample days are reported but not used for the choice.
* **Selected: `rules` {"first_minute": 15, "last_entry_minute": 75, "stop_atr": 4.0, "trail": true, "target_r": null, "take_profit": 0.03, "score": "gain", "min_gain": 0.03, "rvol_min": 1.5, "new_high_minutes": 10, "above_vwap": true, "uptrend": true, "spy_min_gain": 0.003}**
* Out-of-sample check passed: **no**

| Strategy | Params | IS trades | IS net USD | IS max DD % | OOS trades | OOS net USD | OOS win % | All days: move before costs USD | All days: costs USD | Most common rejections |
|---|---|---|---|---|---|---|---|---|---|---|
| rules | `{"first_minute": 15, "last_entry_minute": 75, "stop_atr": 4.0, "trail": true, "target_r": null, "take_profit": 0.03, "score": "gain", "min_gain": 0.03, "rvol_min": 1.5, "new_high_minutes": 10, "above_vwap": true, "uptrend": true, "spy_min_gain": 0.003}` | 7 | 0.6002 | -0.148 | 1 | -0.1088 | 0.0 | +0.7837 | 0.2923 | already have a position or order in this symbol (11); max open positions reached (4); already traded this symbol this session (2) |
| orb | `{"or_minutes": 5, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}` | 4 | 0.4514 | 0.0 | 3 | -0.36 | 0.0 | +0.3723 | 0.2807 | market (56); expected gain 0.056 USD is under 2x costs 0.049 USD (2); expected gain 0.089 USD is under 2x costs 0.059 USD (2) |
| rules | `{"first_minute": 15, "last_entry_minute": 75, "stop_atr": 4.0, "trail": true, "target_r": null, "take_profit": 0.03, "score": "gain", "min_gain": 0.03, "rvol_min": 1.5, "new_high_minutes": 10, "above_vwap": true, "uptrend": true, "min_price": 5.0, "max_vwap_atr": 3.0}` | 2 | 0.0709 | -0.03 | 2 | -0.2399 | 0.0 | -0.0190 | 0.1500 |  |
| rules | `{"first_minute": 45, "last_entry_minute": 90, "stop_atr": 4.0, "trail": true, "target_r": null, "take_profit": 0.03, "score": "gain", "min_gain": 0.03, "rvol_min": 1.5, "new_high_minutes": 10, "above_vwap": true, "uptrend": true}` | 14 | 0.0681 | -0.547 | 12 | -0.7902 | 25.0 | +0.3462 | 1.0683 | already have a position or order in this symbol (32); max open positions reached (12) |
| momentum_leaders | `{"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 4.0, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75}` | 16 | 0.0287 | -0.81 | 11 | -0.4749 | 27.3 | +0.6431 | 1.0892 | already have a position or order in this symbol (29); max open positions reached (11); already traded this symbol this session (2) |
| no_trade | `{}` | 0 | 0.0 | 0.0 | 0 | 0.0 | - | +0.0000 | 0.0000 |  |
| rules | `{"first_minute": 30, "last_entry_minute": 90, "stop_atr": 6.0, "trail": true, "target_r": null, "take_profit": null, "score": "gain", "min_gain": 0.05, "rvol_min": 2.0, "new_high_minutes": 15, "above_vwap": true, "uptrend": true, "spy_above_vwap": true}` | 1 | -0.0787 | -0.155 | 0 | 0.0 | - | -0.0400 | 0.0387 | planned loss for 1 share exceeds the per-trade limit (3) |
| rules | `{"first_minute": 20, "last_entry_minute": 100, "stop_atr": 4.0, "trail": false, "target_r": null, "take_profit": 0.015, "score": "dip", "min_gain": 0.0, "below_vwap_atr": 1.0, "rsi_max": 35, "spy_above_vwap": true}` | 2 | -0.1107 | -0.218 | 6 | -0.6186 | 0.0 | -0.4137 | 0.3156 | already have a position or order in this symbol (17); expected gain 0.060 USD is under 2x costs 0.036 USD (10); expected gain 0.059 USD is under 2x costs 0.036 USD (9) |
| rules | `{"first_minute": 30, "last_entry_minute": 100, "stop_atr": 3.0, "trail": false, "target_r": null, "take_profit": 0.02, "score": "gain", "min_gain": 0.02, "above_vwap": true, "max_vwap_atr": 0.5, "uptrend": true, "spy_min_gain": 0.0}` | 3 | -0.2885 | -0.568 | 0 | 0.0 | - | -0.1646 | 0.1239 | already have a position or order in this symbol (3) |
