# Strategy backtest

Real 1-minute Yahoo bars, same simulator, risk limits and costs as paper trading, starting from 500 SEK.
Only 09:30-11:30 New York time is traded. **This is a short sample and is not evidence of a profitable edge.**

* Data: 2026-09-18 to 2026-10-16; in-sample 14 days, out-of-sample 7 days
* USD/SEK used: 9.9085; starting cash 50.34 USD after conversion fee
* Selection rule: Highest in-sample net P&L after all modeled costs among variants with >= 5 in-sample trades; out-of-sample days are reported but not used for the choice.
* **Selected: `momentum_leaders` {"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 2.0, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75}**
* Out-of-sample check passed: **no**

| Strategy | Params | IS trades | IS net USD | IS max DD % | OOS trades | OOS net USD | OOS win % | Most common rejections |
|---|---|---|---|---|---|---|---|---|
| no_trade | `{}` | 0 | 0.0 | 0.0 | 0 | 0.0 | - |  |
| momentum_leaders | `{"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 2.0, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75}` | 8 | -0.1834 | -0.437 | 8 | -0.5552 | 12.5 | already have a position or order in this symbol (12); already traded this symbol this session (6) |
| momentum_leaders | `{"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 2.0, "take_profit": 0.08, "first_minute": 15, "last_entry_minute": 75}` | 8 | -0.1834 | -0.437 | 8 | -0.5552 | 12.5 | already have a position or order in this symbol (12); already traded this symbol this session (6) |
| momentum_leaders | `{"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 4.0, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75}` | 8 | -0.4788 | -0.951 | 8 | -0.0804 | 37.5 | already have a position or order in this symbol (18) |
| momentum_leaders | `{"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 4.0, "take_profit": 0.08, "first_minute": 15, "last_entry_minute": 75}` | 8 | -0.4788 | -0.951 | 8 | 0.1382 | 37.5 | already have a position or order in this symbol (18) |
| orb | `{"or_minutes": 5, "rvol_min": 2.0, "target_r": 2.5, "stop_atr": 2.0, "last_entry_minute": 90}` | 15 | -0.7321 | -1.791 | 6 | -0.4223 | 16.7 | already traded this symbol this session (3); expected gain 0.071 USD is under 2x costs 0.060 USD (2); already have a position or order in this symbol (2) |
| momentum_leaders | `{"min_gain": 0.015, "rvol_min": 1.5, "trail_atr": 2.0, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75}` | 21 | -0.8442 | -1.713 | 22 | -1.5291 | 4.5 | already have a position or order in this symbol (27); already traded this symbol this session (24); max entries per session reached (10) |
| momentum_leaders | `{"min_gain": 0.015, "rvol_min": 1.5, "trail_atr": 2.0, "take_profit": 0.08, "first_minute": 15, "last_entry_minute": 75}` | 21 | -0.8442 | -1.713 | 22 | -1.5291 | 4.5 | already have a position or order in this symbol (27); already traded this symbol this session (24); max entries per session reached (10) |
| momentum_leaders | `{"min_gain": 0.015, "rvol_min": 1.5, "trail_atr": 4.0, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75}` | 20 | -1.2228 | -2.429 | 17 | -0.6959 | 35.3 | already have a position or order in this symbol (46); max open positions reached (21) |
| momentum_leaders | `{"min_gain": 0.015, "rvol_min": 1.5, "trail_atr": 4.0, "take_profit": 0.08, "first_minute": 15, "last_entry_minute": 75}` | 20 | -1.2228 | -2.429 | 17 | -0.7192 | 35.3 | already have a position or order in this symbol (46); max open positions reached (21) |
