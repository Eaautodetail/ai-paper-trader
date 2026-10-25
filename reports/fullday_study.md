# Study: later daily deadline (research only, live schedule unchanged)

History: 21 trading days of real Yahoo 1-minute bars (2026-09-25..2026-10-23).

## 1. Real trades sold at the 11:30 deadline, replayed as if kept (same stop/target) until 16:00

| Day | Stock | Shares | Entry | Sold at 11:30 | Net then | If kept: exit | How | Time NY | Net if kept |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-15 | MARA | 1 | 8.0340 | 8.0060 | -0.0480 | 7.9521 | stop | 11:56 | -0.1019 |
| 2026-10-20 | ABEV | 3 | 3.3016 | 3.3283 | +0.0601 | 3.3233 | close | 15:59 | +0.0451 |
| 2026-10-20 | GRAB | 3 | 2.9065 | 2.8786 | -0.1037 | 2.8600 | stop | 12:29 | -0.1592 |
| 2026-10-21 | SNAP | 1 | 6.4132 | 6.4018 | -0.0314 | 6.3328 | stop | 14:50 | -0.1004 |

## 2. Backtest: same rules, different deadline

| Strategy | Buys allowed | Deadline (NY) | Trades | Net USD after costs | Older days | Recent days | Move before costs | Costs | Worst drawdown % |
|---|---|---|---|---|---|---|---|---|---|
| momentum_leaders | buys in first ~1.5 h | 11:30 | 25 | -0.097 | -0.4846 | 0.3878 | +0.890 | 0.987 | -0.991 |
| momentum_leaders | buys in first ~1.5 h | 13:00 | 25 | -0.315 | -0.5445 | 0.2295 | +0.663 | 0.978 | -1.11 |
| momentum_leaders | buys in first ~1.5 h | 14:30 | 25 | -0.355 | -0.5821 | 0.2268 | +0.610 | 0.965 | -1.185 |
| momentum_leaders | buys in first ~1.5 h | 15:55 | 25 | -0.373 | -0.6 | 0.2268 | +0.592 | 0.965 | -1.22 |
| momentum_leaders | may also buy until 15:00 | 13:00 | 42 | -1.221 | -0.8587 | -0.3623 | +0.498 | 1.719 | -1.709 |
| momentum_leaders | may also buy until 15:00 | 14:30 | 46 | -1.348 | -1.0927 | -0.2553 | +0.562 | 1.910 | -2.174 |
| momentum_leaders | may also buy until 15:00 | 15:55 | 51 | -1.601 | -1.4642 | -0.1365 | +0.506 | 2.106 | -2.913 |
| orb | buys in first ~1.5 h | 11:30 | 31 | -1.691 | -1.1168 | -0.5737 | -0.266 | 1.425 | -2.469 |
| orb | buys in first ~1.5 h | 13:00 | 30 | -1.770 | -1.1323 | -0.6381 | -0.396 | 1.375 | -2.499 |
| orb | buys in first ~1.5 h | 14:30 | 30 | -1.887 | -1.0921 | -0.7945 | -0.512 | 1.375 | -2.42 |
| orb | buys in first ~1.5 h | 15:55 | 30 | -2.009 | -1.2021 | -0.8065 | -0.634 | 1.375 | -2.638 |
| orb | may also buy until 15:00 | 13:00 | 37 | -2.099 | -1.2634 | -0.8351 | -0.386 | 1.712 | -2.76 |
| orb | may also buy until 15:00 | 14:30 | 40 | -2.312 | -1.1463 | -1.1662 | -0.446 | 1.867 | -2.831 |
| orb | may also buy until 15:00 | 15:55 | 39 | -2.290 | -1.1115 | -1.1781 | -0.473 | 1.817 | -2.855 |

_Each run starts from 500 SEK. Past results do not guarantee future results._
