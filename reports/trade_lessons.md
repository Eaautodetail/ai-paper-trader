# Trade lessons

What winning and losing trades had in common at the moment of buying. Analysis only: a pattern becomes a rule only after it is added as a fixed strategy variant and passes the weekly walk-forward test.

## Real paper trades

All simulated trades so far, updated after every session.

* Trades: 15; winners: 13.3%; total net after costs: -0.963 USD
* Average price move before costs: -0.27% per trade; average costs: 0.54% per trade
* How trades ended: stop 11, window_end 3, target 1

**What stands out** (groups of at least 5 trades):

* Stock's gain since the open, %: best when **0 to 1** (6 trades, 17% winners, avg -0.068 USD), worst when **3 to 5** (5 trades, 0% winners, avg -0.092 USD)
* Costs as % of the trade: best when **0.5 to 0.75** (10 trades, 20% winners, avg -0.040 USD), worst when **0.3 to 0.5** (5 trades, 0% winners, avg -0.114 USD)
* Share price, USD: best when **3 to 5** (5 trades, 20% winners, avg -0.066 USD), worst when **8 to 12** (5 trades, 0% winners, avg -0.114 USD)

<details><summary>Minutes after the open</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 15 | 3 | 33 | -0.0450 | -0.1350 | -0.17 |
| 15 to 30 | 2 | 0 | -0.1115 | -0.2230 | -0.86 |
| 30 to 45 | 2 | 0 | -0.0901 | -0.1802 | -0.53 |
| 45 to 60 | 6 | 17 | -0.0449 | -0.2694 | +0.03 |
| 60 to 90 | 2 | 0 | -0.0778 | -0.1557 | -0.42 |

</details>

<details><summary>Stock's gain since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 1 | 6 | 17 | -0.0684 | -0.4107 | -0.24 |
| 1 to 2 | 4 | 25 | -0.0236 | -0.0944 | +0.11 |
| 3 to 5 | 5 | 0 | -0.0916 | -0.4581 | -0.60 |

</details>

<details><summary>Volume vs normal (x)</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 1.5 to 2 | 4 | 0 | -0.0826 | -0.3304 | -0.50 |
| 2 to 3 | 5 | 20 | -0.0645 | -0.3224 | -0.35 |
| 3 to 5 | 3 | 0 | -0.1118 | -0.3353 | -0.74 |
| 5 or more | 3 | 33 | +0.0083 | +0.0248 | +0.65 |

</details>

<details><summary>Price above VWAP, in ATRs</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 1 | 2 | 50 | +0.0143 | +0.0286 | +0.64 |
| 1 to 2 | 4 | 25 | -0.0197 | -0.0789 | +0.25 |
| 2 to 3 | 3 | 0 | -0.0671 | -0.2013 | -0.33 |
| 3 or more | 6 | 0 | -0.1186 | -0.7117 | -0.88 |

</details>

<details><summary>Volatility: 1-min ATR as % of price</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.2 to 0.3 | 1 | 0 | -0.1138 | -0.1138 | -0.81 |
| 0.3 to 0.5 | 12 | 8 | -0.0815 | -0.9780 | -0.45 |
| 0.5 or more | 2 | 50 | +0.0643 | +0.1286 | +1.09 |

</details>

<details><summary>Market (SPY) since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| -0.3 to 0 | 4 | 25 | -0.0400 | -0.1600 | -0.02 |
| 0 to 0.3 | 7 | 0 | -0.1032 | -0.7225 | -0.78 |
| 0.3 or more | 4 | 25 | -0.0202 | -0.0807 | +0.38 |

</details>

<details><summary>Costs as % of the trade</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.3 to 0.5 | 5 | 0 | -0.1136 | -0.5679 | -0.86 |
| 0.5 to 0.75 | 10 | 20 | -0.0395 | -0.3953 | +0.03 |

</details>

<details><summary>Share price, USD</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 3 | 2 | 50 | +0.0580 | +0.1161 | +1.35 |
| 3 to 5 | 5 | 20 | -0.0656 | -0.3280 | -0.22 |
| 5 to 8 | 3 | 0 | -0.0612 | -0.1835 | -0.43 |
| 8 to 12 | 5 | 0 | -0.1136 | -0.5679 | -0.86 |

</details>

## Current strategy replayed on all stored history

Strategy `{"name": "momentum_leaders", "params": {"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 4.0, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75}}` over 21 trading days, updated by the weekly review. Larger sample, so patterns here are more reliable than in the real trades.

* Trades: 23; winners: 39.1%; total net after costs: -0.046 USD
* Average price move before costs: +0.51% per trade; average costs: 0.58% per trade
* How trades ended: stop 13, window_end 5, target 5

**What stands out** (groups of at least 5 trades):

* Minutes after the open: best when **45 to 60** (7 trades, 43% winners, avg +0.005 USD), worst when **15 to 30** (9 trades, 22% winners, avg -0.067 USD)
* Volume vs normal (x): best when **1.5 to 2** (9 trades, 44% winners, avg +0.032 USD), worst when **2 to 3** (6 trades, 33% winners, avg -0.037 USD)
* Market (SPY) since the open, %: best when **0.3 or more** (7 trades, 57% winners, avg +0.089 USD), worst when **-0.3 to 0** (8 trades, 12% winners, avg -0.080 USD)
* Costs as % of the trade: best when **0.3 to 0.5** (6 trades, 67% winners, avg +0.105 USD), worst when **0.5 to 0.75** (16 trades, 31% winners, avg -0.034 USD)
* Share price, USD: best when **5 to 8** (10 trades, 40% winners, avg +0.005 USD), worst when **3 to 5** (7 trades, 29% winners, avg -0.049 USD)

<details><summary>Minutes after the open</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 15 to 30 | 9 | 22 | -0.0668 | -0.6011 | -0.36 |
| 30 to 45 | 3 | 100 | +0.1989 | +0.5967 | +3.05 |
| 45 to 60 | 7 | 43 | +0.0051 | +0.0358 | +0.64 |
| 60 to 90 | 4 | 25 | -0.0194 | -0.0776 | +0.30 |

</details>

<details><summary>Stock's gain since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 3 to 5 | 22 | 36 | -0.0103 | -0.2256 | +0.39 |
| 5 or more | 1 | 100 | +0.1794 | +0.1794 | +3.15 |

</details>

<details><summary>Volume vs normal (x)</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 1.5 to 2 | 9 | 44 | +0.0317 | +0.2853 | +0.89 |
| 2 to 3 | 6 | 33 | -0.0370 | -0.2219 | -0.10 |
| 3 to 5 | 4 | 25 | -0.0880 | -0.3521 | -0.47 |
| 5 or more | 4 | 50 | +0.0606 | +0.2425 | +1.53 |

</details>

<details><summary>Price above VWAP, in ATRs</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 2 to 3 | 2 | 0 | -0.0756 | -0.1513 | -0.84 |
| 3 or more | 21 | 43 | +0.0050 | +0.1051 | +0.63 |

</details>

<details><summary>Volatility: 1-min ATR as % of price</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.2 to 0.3 | 1 | 0 | -0.0632 | -0.0632 | -0.52 |
| 0.3 to 0.5 | 19 | 37 | -0.0070 | -0.1337 | +0.44 |
| 0.5 or more | 3 | 67 | +0.0503 | +0.1508 | +1.29 |

</details>

<details><summary>Market (SPY) since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| -0.3 to 0 | 8 | 12 | -0.0803 | -0.6423 | -0.57 |
| 0 to 0.3 | 8 | 50 | -0.0036 | -0.0288 | +0.62 |
| 0.3 or more | 7 | 57 | +0.0893 | +0.6249 | +1.61 |

</details>

<details><summary>Costs as % of the trade</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.3 to 0.5 | 6 | 67 | +0.1053 | +0.6316 | +1.82 |
| 0.5 to 0.75 | 16 | 31 | -0.0337 | -0.5386 | +0.17 |
| 0.75 to 1 | 1 | 0 | -0.1392 | -0.1392 | -1.99 |

</details>

<details><summary>Share price, USD</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 3 | 2 | 50 | -0.0045 | -0.0091 | +0.38 |
| 3 to 5 | 7 | 29 | -0.0486 | -0.3399 | +0.05 |
| 5 to 8 | 10 | 40 | +0.0046 | +0.0458 | +0.57 |
| 8 to 12 | 4 | 50 | +0.0642 | +0.2569 | +1.19 |

</details>
