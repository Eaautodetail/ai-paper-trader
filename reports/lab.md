# Strategy lab

Extra simulated accounts, each with its own 500 SEK of play money, trading the same sessions as the main account with the same costs, limits and 11:30 deadline. They never affect the main account. A lab strategy is only worth promoting after many sessions; a few good days are often luck.

Retirement rule (fixed): judged only after 20 sessions and 15 trades; retired if losing with profit factor below 0.8, or still losing after 40 sessions. Winners keep going. A retired account stops trading but its record is kept, so the lessons are not lost.

| Rank | Lab account | Sessions | Trades | Winners | Net after costs USD | Account SEK | Active | Idea |
|---|---|---|---|---|---|---|---|---|
| 1 | orb_market_filter | 5 | 1 | 100% | +0.228 | 498.85 | yes | Opening-range breakout that only buys while the market is above its VWAP (top of the weekly review list on 2026-10-17) |
| 2 | vwap_pullback_leader | 4 | 2 | 50% | -0.039 | 499.93 | yes | Instead of buying at a new high (where real losers often bought 4-5 ATR above VWAP), wait until a stock that is up 2%+ pulls back close to VWAP, with the market up, and aim for +2% |
| 3 | momentum_no_chasing | 5 | 1 | 0% | -0.104 | 495.59 | yes | Current momentum rules, but skip stocks under 5 USD (higher costs) and stocks already far above VWAP (real losers were 4-5 ATR above) |
| 4 | big_mover_ride | 4 | 2 | 0% | -0.138 | 498.95 | yes | Costs (~0.55%) eat the small +0.36% average move, so only take the day's very strongest movers (up 5%+) in a strong market and let a wide trailing stop ride the trend for a bigger move per trade |
| 5 | dip_buy_strong_market | 5 | 3 | 0% | -0.218 | 494.48 | yes | Different style: buy a short dip below VWAP in a stock that is still up on the day, only while the market is strong; aims for +1.5% |
| 6 | momentum_later_entry | 5 | 7 | 29% | -0.339 | 493.30 | yes | Current momentum rules, but buy 45-90 min after the open (15-30 min was the worst group) |
| 7 | momentum_market_up | 5 | 6 | 17% | -0.434 | 492.37 | yes | Current momentum rules, but only buy when the whole market is up at least 0.3% (best group in the trade lessons) |

## Rules each account uses

* **orb_market_filter** (added 2026-10-29): `{"name": "orb", "params": {"or_minutes": 5, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}}`
* **vwap_pullback_leader** (added 2026-10-31): `{"name": "rules", "params": {"min_gain": 0.02, "above_vwap": true, "max_vwap_atr": 0.5, "uptrend": true, "spy_min_gain": 0.0, "stop_atr": 3.0, "trail": false, "target_r": null, "take_profit": 0.02, "first_minute": 30, "last_entry_minute": 100, "score": "gain"}}`
* **momentum_no_chasing** (added 2026-10-29): `{"name": "rules", "params": {"min_gain": 0.03, "rvol_min": 1.5, "new_high_minutes": 10, "above_vwap": true, "uptrend": true, "stop_atr": 4.0, "trail": true, "target_r": null, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75, "score": "gain", "min_price": 5.0, "max_vwap_atr": 3.0}}`
* **big_mover_ride** (added 2026-10-31): `{"name": "rules", "params": {"min_gain": 0.05, "rvol_min": 2.0, "new_high_minutes": 15, "above_vwap": true, "uptrend": true, "spy_above_vwap": true, "stop_atr": 6.0, "trail": true, "target_r": null, "take_profit": null, "first_minute": 30, "last_entry_minute": 90, "score": "gain"}}`
* **dip_buy_strong_market** (added 2026-10-29): `{"name": "rules", "params": {"min_gain": 0.0, "below_vwap_atr": 1.0, "rsi_max": 35, "spy_above_vwap": true, "stop_atr": 4.0, "trail": false, "target_r": null, "first_minute": 20, "last_entry_minute": 100, "score": "dip", "take_profit": 0.015}}`
* **momentum_later_entry** (added 2026-10-29): `{"name": "rules", "params": {"min_gain": 0.03, "rvol_min": 1.5, "new_high_minutes": 10, "above_vwap": true, "uptrend": true, "stop_atr": 4.0, "trail": true, "target_r": null, "take_profit": 0.03, "first_minute": 45, "last_entry_minute": 90, "score": "gain"}}`
* **momentum_market_up** (added 2026-10-29): `{"name": "rules", "params": {"min_gain": 0.03, "rvol_min": 1.5, "new_high_minutes": 10, "above_vwap": true, "uptrend": true, "stop_atr": 4.0, "trail": true, "target_r": null, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75, "score": "gain", "spy_min_gain": 0.003}}`
