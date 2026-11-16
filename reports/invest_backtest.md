# Long-term investing: backtest (research only)

Real daily prices 2022-08-30 .. 2026-11-12. Older period (rules chosen here) until 2025-06-23, recent period after it (only reported). Each run starts from 500 SEK.

**Important:** the watchlist was picked today, knowing which companies did well (for example NVIDIA). That makes every test on this list look better than reality. Compare with simply buying and holding, which has the same bias.

| Strategy | Settings | Older: return | Older: worst drop | Older: trades | Older: profit factor | Recent: return | Recent: worst drop | Recent: trades | Recent: profit factor |
|---|---|---|---|---|---|---|---|---|---|
| **buy and hold QQQ** | (benchmark) | +78.4% | -22.8% | 0 | - | +25.4% | -14.8% | 0 | - |
| **buy and hold the whole watchlist (equal parts)** | (benchmark) | +299.9% | -32.3% | 0 | - | +45.4% | -31.0% | 0 | - |
| trend_breakout (selected) | `{"stop_atr": 2.5, "trail_atr": 3.5, "take_profit": null, "max_hold_days": 120, "trend_exit": true}` | +44.1% | -10.4% | 103 | 2.29 | +3.5% | -12.3% | 83 | 1.15 |
| quality_dip | `{"dip_pct": 0.08, "rsi_max": 45, "stop_atr": 3.0, "trail_atr": 4.0, "take_profit": null, "max_hold_days": 60, "trend_exit": true}` | +34.4% | -8.2% | 115 | 2.25 | +9.4% | -6.0% | 76 | 1.69 |
| quality_dip | `{"dip_pct": 0.08, "rsi_max": 45, "stop_atr": 3.0, "trail_atr": 4.0, "take_profit": 0.25, "max_hold_days": 60, "trend_exit": true}` | +24.0% | -6.1% | 121 | 2.01 | +6.3% | -5.3% | 78 | 1.44 |
| trend_breakout | `{"stop_atr": 4.0, "trail_atr": 5.0, "take_profit": null, "max_hold_days": 120, "trend_exit": true}` | +21.8% | -8.9% | 64 | 2.37 | +8.0% | -7.7% | 48 | 1.8 |
| quality_dip | `{"dip_pct": 0.15, "rsi_max": 45, "stop_atr": 3.0, "trail_atr": 4.0, "take_profit": null, "max_hold_days": 60, "trend_exit": true}` | +13.5% | -5.5% | 60 | 2.14 | +8.6% | -5.3% | 41 | 2.62 |
| quality_dip | `{"dip_pct": 0.08, "rsi_max": 35, "stop_atr": 3.0, "trail_atr": 4.0, "take_profit": 0.25, "max_hold_days": 60, "trend_exit": true}` | +11.7% | -4.1% | 44 | 2.39 | +1.4% | -2.6% | 25 | 1.32 |
| quality_dip | `{"dip_pct": 0.08, "rsi_max": 35, "stop_atr": 3.0, "trail_atr": 4.0, "take_profit": null, "max_hold_days": 60, "trend_exit": true}` | +10.7% | -6.3% | 44 | 2.27 | +4.8% | -2.6% | 25 | 2.08 |
| quality_dip | `{"dip_pct": 0.15, "rsi_max": 35, "stop_atr": 3.0, "trail_atr": 4.0, "take_profit": 0.25, "max_hold_days": 60, "trend_exit": true}` | +8.1% | -2.0% | 27 | 3.19 | +3.2% | -1.6% | 12 | 3.8 |
| quality_dip | `{"dip_pct": 0.15, "rsi_max": 45, "stop_atr": 3.0, "trail_atr": 4.0, "take_profit": 0.25, "max_hold_days": 60, "trend_exit": true}` | +8.0% | -4.5% | 62 | 1.83 | +7.7% | -3.7% | 42 | 2.35 |
| quality_dip | `{"dip_pct": 0.15, "rsi_max": 35, "stop_atr": 3.0, "trail_atr": 4.0, "take_profit": null, "max_hold_days": 60, "trend_exit": true}` | +7.2% | -3.2% | 27 | 2.97 | +4.1% | -1.6% | 12 | 4.63 |

_Return = change of the whole 500 SEK account in USD. Worst drop = largest fall from a high. Past results do not guarantee future results._
