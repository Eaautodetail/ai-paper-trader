# Strategy backtest

Real 1-minute Yahoo bars, same simulator, risk limits and costs as paper trading, starting from 500 SEK.
Only 09:30-11:30 New York time is traded. **This is a short sample and is not evidence of a profitable edge.**
If 'move before costs' is negative, the strategy lost before any fees, so a bigger trade size would only lose more.

* Data: 2026-09-18 to 2026-10-16; in-sample 14 days, out-of-sample 7 days
* USD/SEK used: 9.9085; starting cash 50.34 USD after conversion fee
* Selection rule: Highest in-sample net P&L after all modeled costs among variants with >= 5 in-sample trades; out-of-sample days are reported but not used for the choice.
* **Selected: `momentum_leaders` {"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 2.0, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75}**
* Out-of-sample check passed: **no**

| Strategy | Params | IS trades | IS net USD | IS max DD % | OOS trades | OOS net USD | OOS win % | All days: move before costs USD | All days: costs USD | Most common rejections |
|---|---|---|---|---|---|---|---|---|---|---|
| no_trade | `{}` | 0 | 0.0 | 0.0 | 0 | 0.0 | - | +0.0000 | 0.0000 |  |
| momentum_leaders | `{"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 2.0, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75}` | 8 | -0.266 | -0.623 | 8 | -0.5688 | 12.5 | -0.1413 | 0.6935 | already have a position or order in this symbol (12); already traded this symbol this session (6) |
| momentum_leaders | `{"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 2.0, "take_profit": 0.08, "first_minute": 15, "last_entry_minute": 75}` | 8 | -0.266 | -0.623 | 8 | -0.5688 | 12.5 | -0.1413 | 0.6935 | already have a position or order in this symbol (12); already traded this symbol this session (6) |
| orb | `{"or_minutes": 5, "rvol_min": 2.0, "target_r": 2.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 14 | -0.606 | -1.542 | 6 | -0.4223 | 16.7 | -0.0919 | 0.9363 | already traded this symbol this session (3); expected gain 0.071 USD is under 2x costs 0.060 USD (2); already have a position or order in this symbol (2) |
| momentum_leaders | `{"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 4.0, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75}` | 8 | -0.623 | -1.238 | 8 | -0.0906 | 37.5 | -0.0750 | 0.6386 | already have a position or order in this symbol (18) |
| momentum_leaders | `{"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 4.0, "take_profit": 0.08, "first_minute": 15, "last_entry_minute": 75}` | 8 | -0.623 | -1.238 | 8 | 0.128 | 37.5 | +0.1619 | 0.6569 | already have a position or order in this symbol (18) |
| momentum_leaders | `{"min_gain": 0.015, "rvol_min": 1.5, "trail_atr": 2.0, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75}` | 19 | -0.9602 | -1.926 | 20 | -1.1108 | 10.0 | -0.3544 | 1.7165 | already have a position or order in this symbol (27); already traded this symbol this session (25); max entries per session reached (8) |
| momentum_leaders | `{"min_gain": 0.015, "rvol_min": 1.5, "trail_atr": 2.0, "take_profit": 0.08, "first_minute": 15, "last_entry_minute": 75}` | 19 | -0.9602 | -1.926 | 20 | -1.2137 | 10.0 | -0.4332 | 1.7406 | already have a position or order in this symbol (27); already traded this symbol this session (25); max entries per session reached (8) |
| momentum_leaders | `{"min_gain": 0.015, "rvol_min": 1.5, "trail_atr": 4.0, "take_profit": 0.08, "first_minute": 15, "last_entry_minute": 75}` | 18 | -1.17 | -2.324 | 16 | -0.7148 | 31.2 | -0.4059 | 1.4789 | already have a position or order in this symbol (46); max open positions reached (19) |
| momentum_leaders | `{"min_gain": 0.015, "rvol_min": 1.5, "trail_atr": 4.0, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75}` | 18 | -1.2009 | -2.386 | 16 | -0.6916 | 31.2 | -0.4348 | 1.4577 | already have a position or order in this symbol (46); max open positions reached (19) |
