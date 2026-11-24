# Trade lessons

What winning and losing trades had in common at the moment of buying. Analysis only: a pattern becomes a rule only after it is added as a fixed strategy variant and passes the weekly walk-forward test.

## Real paper trades

All simulated trades so far, updated after every session.

* Trades: 35; winners: 14.3%; total net after costs: -2.407 USD
* Average price move before costs: -0.48% per trade; average costs: 0.61% per trade
* How trades ended: stop 25, window_end 8, target 2

**What stands out** (groups of at least 5 trades):

* Minutes after the open: best when **45 to 60** (12 trades, 17% winners, avg -0.061 USD), worst when **30 to 45** (6 trades, 0% winners, avg -0.088 USD)
* Stock's gain since the open, %: best when **1 to 2** (6 trades, 17% winners, avg -0.051 USD), worst when **0 to 1** (8 trades, 12% winners, avg -0.076 USD)
* Volume vs normal (x): best when **1.5 to 2** (9 trades, 22% winners, avg -0.051 USD), worst when **3 to 5** (6 trades, 0% winners, avg -0.108 USD)
* Price above VWAP, in ATRs: best when **1 to 2** (7 trades, 14% winners, avg -0.061 USD), worst when **2 to 3** (5 trades, 0% winners, avg -0.092 USD)
* Volatility: 1-min ATR as % of price: best when **0.5 or more** (10 trades, 20% winners, avg -0.050 USD), worst when **0.3 to 0.5** (24 trades, 12% winners, avg -0.075 USD)
* Market (SPY) since the open, %: best when **-0.3 to 0** (5 trades, 20% winners, avg -0.034 USD), worst when **0.3 or more** (18 trades, 11% winners, avg -0.076 USD)
* Costs as % of the trade: best when **0.3 to 0.5** (8 trades, 25% winners, avg -0.061 USD), worst when **0.5 to 0.75** (23 trades, 13% winners, avg -0.065 USD)
* Share price, USD: best when **0 to 3** (5 trades, 40% winners, avg -0.018 USD), worst when **8 to 12** (6 trades, 0% winners, avg -0.120 USD)

<details><summary>Minutes after the open</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 15 | 3 | 33 | -0.0450 | -0.1350 | -0.17 |
| 15 to 30 | 9 | 11 | -0.0759 | -0.6828 | -0.79 |
| 30 to 45 | 6 | 0 | -0.0883 | -0.5298 | -0.59 |
| 45 to 60 | 12 | 17 | -0.0613 | -0.7352 | -0.32 |
| 60 to 90 | 5 | 20 | -0.0649 | -0.3245 | -0.38 |

</details>

<details><summary>Stock's gain since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 1 | 8 | 12 | -0.0755 | -0.6041 | -0.40 |
| 1 to 2 | 6 | 17 | -0.0514 | -0.3083 | -0.20 |
| 2 to 3 | 1 | 0 | -0.1361 | -0.1361 | -1.07 |
| 3 to 5 | 15 | 13 | -0.0675 | -1.0120 | -0.38 |
| 5 or more | 5 | 20 | -0.0693 | -0.3467 | -1.13 |

</details>

<details><summary>Volume vs normal (x)</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 1.5 to 2 | 9 | 22 | -0.0507 | -0.4564 | -0.47 |
| 2 to 3 | 16 | 12 | -0.0761 | -1.2170 | -0.59 |
| 3 to 5 | 6 | 0 | -0.1080 | -0.6479 | -0.72 |
| 5 or more | 4 | 25 | -0.0215 | -0.0860 | +0.26 |

</details>

<details><summary>Price above VWAP, in ATRs</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 1 | 4 | 25 | -0.0506 | -0.2023 | -0.18 |
| 1 to 2 | 7 | 14 | -0.0609 | -0.4262 | -0.37 |
| 2 to 3 | 5 | 0 | -0.0924 | -0.4621 | -1.07 |
| 3 or more | 19 | 16 | -0.0693 | -1.3167 | -0.44 |

</details>

<details><summary>Volatility: 1-min ATR as % of price</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.2 to 0.3 | 1 | 0 | -0.1138 | -0.1138 | -0.81 |
| 0.3 to 0.5 | 24 | 12 | -0.0747 | -1.7926 | -0.43 |
| 0.5 or more | 10 | 20 | -0.0501 | -0.5008 | -0.58 |

</details>

<details><summary>Market (SPY) since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| -0.3 to 0 | 5 | 20 | -0.0339 | -0.1696 | +0.07 |
| 0 to 0.3 | 12 | 17 | -0.0731 | -0.8774 | -0.42 |
| 0.3 or more | 18 | 11 | -0.0756 | -1.3603 | -0.68 |

</details>

<details><summary>Costs as % of the trade</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.3 to 0.5 | 8 | 25 | -0.0614 | -0.4911 | -0.17 |
| 0.5 to 0.75 | 23 | 13 | -0.0650 | -1.4952 | -0.39 |
| 0.75 to 1 | 3 | 0 | -0.0988 | -0.2963 | -1.07 |
| 1 or more | 1 | 0 | -0.1247 | -0.1247 | -3.29 |

</details>

<details><summary>Share price, USD</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 3 | 5 | 40 | -0.0178 | -0.0889 | +0.00 |
| 3 to 5 | 13 | 8 | -0.0796 | -1.0342 | -0.56 |
| 5 to 8 | 11 | 18 | -0.0512 | -0.5632 | -0.37 |
| 8 to 12 | 6 | 0 | -0.1202 | -0.7210 | -0.92 |

</details>

## Current strategy replayed on all stored history

Strategy `{"name": "orb", "params": {"or_minutes": 5, "rvol_min": 1.2, "target_r": 1.5, "stop_atr": 2.0, "last_entry_minute": 90}}` over 25 trading days, updated by the weekly review. Larger sample, so patterns here are more reliable than in the real trades.

* Trades: 21; winners: 42.9%; total net after costs: -0.140 USD
* Average price move before costs: +0.30% per trade; average costs: 0.48% per trade
* How trades ended: stop 10, target 9, window_end 2

**What stands out** (groups of at least 5 trades):

* Minutes after the open: best when **15 to 30** (8 trades, 75% winners, avg +0.088 USD), worst when **0 to 15** (8 trades, 25% winners, avg -0.049 USD)
* Stock's gain since the open, %: best when **0 to 1** (7 trades, 57% winners, avg +0.016 USD), worst when **2 to 3** (7 trades, 29% winners, avg -0.055 USD)
* Volume vs normal (x): best when **2 to 3** (5 trades, 40% winners, avg +0.001 USD), worst when **1.5 to 2** (7 trades, 29% winners, avg -0.056 USD)
* Price above VWAP, in ATRs: best when **1 to 2** (9 trades, 56% winners, avg +0.045 USD), worst when **3 or more** (5 trades, 40% winners, avg -0.039 USD)
* Market (SPY) since the open, %: best when **0.3 or more** (5 trades, 60% winners, avg +0.023 USD), worst when **-0.3 to 0** (5 trades, 20% winners, avg -0.094 USD)
* Costs as % of the trade: best when **0.3 to 0.5** (13 trades, 69% winners, avg +0.065 USD), worst when **0.5 to 0.75** (8 trades, 0% winners, avg -0.123 USD)
* Share price, USD: best when **3 to 5** (7 trades, 57% winners, avg +0.042 USD), worst when **5 to 8** (9 trades, 33% winners, avg -0.034 USD)

<details><summary>Minutes after the open</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 15 | 8 | 25 | -0.0489 | -0.3914 | -0.23 |
| 15 to 30 | 8 | 75 | +0.0878 | +0.7028 | +1.44 |
| 30 to 45 | 3 | 0 | -0.1419 | -0.4258 | -1.31 |
| 60 to 90 | 2 | 50 | -0.0129 | -0.0257 | +0.30 |

</details>

<details><summary>Stock's gain since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 1 | 7 | 57 | +0.0160 | +0.1123 | +0.46 |
| 1 to 2 | 3 | 33 | -0.0201 | -0.0604 | +0.32 |
| 2 to 3 | 7 | 29 | -0.0546 | -0.3823 | -0.29 |
| 3 to 5 | 3 | 33 | -0.0217 | -0.0652 | +0.14 |
| 5 or more | 1 | 100 | +0.2555 | +0.2555 | +3.78 |

</details>

<details><summary>Volume vs normal (x)</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 1.5 | 4 | 75 | +0.0764 | +0.3056 | +1.15 |
| 1.5 to 2 | 7 | 29 | -0.0557 | -0.3898 | -0.37 |
| 2 to 3 | 5 | 40 | +0.0012 | +0.0058 | +0.67 |
| 3 to 5 | 5 | 40 | -0.0123 | -0.0617 | +0.21 |

</details>

<details><summary>Price above VWAP, in ATRs</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 1 | 4 | 25 | -0.0898 | -0.3594 | -0.62 |
| 1 to 2 | 9 | 56 | +0.0453 | +0.4080 | +0.87 |
| 2 to 3 | 3 | 33 | +0.0017 | +0.0051 | +0.51 |
| 3 or more | 5 | 40 | -0.0388 | -0.1938 | -0.10 |

</details>

<details><summary>Volatility: 1-min ATR as % of price</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.3 to 0.5 | 2 | 50 | -0.0129 | -0.0257 | +0.30 |
| 0.5 or more | 19 | 42 | -0.0060 | -0.1144 | +0.30 |

</details>

<details><summary>Market (SPY) since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| below -0.3 | 1 | 100 | +0.1216 | +0.1216 | +1.75 |
| -0.3 to 0 | 5 | 20 | -0.0939 | -0.4693 | -0.92 |
| 0 to 0.3 | 10 | 40 | +0.0091 | +0.0908 | +0.52 |
| 0.3 or more | 5 | 60 | +0.0233 | +0.1167 | +0.80 |

</details>

<details><summary>Costs as % of the trade</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.3 to 0.5 | 13 | 69 | +0.0648 | +0.8422 | +1.22 |
| 0.5 to 0.75 | 8 | 0 | -0.1228 | -0.9823 | -1.18 |

</details>

<details><summary>Share price, USD</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 3 to 5 | 7 | 57 | +0.0420 | +0.2942 | +0.97 |
| 5 to 8 | 9 | 33 | -0.0343 | -0.3090 | -0.07 |
| 8 to 12 | 5 | 40 | -0.0251 | -0.1253 | +0.05 |

</details>
