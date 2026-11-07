# Trade lessons

What winning and losing trades had in common at the moment of buying. Analysis only: a pattern becomes a rule only after it is added as a fixed strategy variant and passes the weekly walk-forward test.

## Real paper trades

All simulated trades so far, updated after every session.

* Trades: 28; winners: 17.9%; total net after costs: -1.590 USD
* Average price move before costs: -0.27% per trade; average costs: 0.58% per trade
* How trades ended: stop 18, window_end 8, target 2

**What stands out** (groups of at least 5 trades):

* Minutes after the open: best when **45 to 60** (12 trades, 17% winners, avg -0.061 USD), worst when **30 to 45** (5 trades, 0% winners, avg -0.079 USD)
* Stock's gain since the open, %: best when **3 to 5** (14 trades, 14% winners, avg -0.062 USD), worst when **0 to 1** (6 trades, 17% winners, avg -0.068 USD)
* Volume vs normal (x): best when **1.5 to 2** (8 trades, 25% winners, avg -0.041 USD), worst when **2 to 3** (13 trades, 15% winners, avg -0.070 USD)
* Volatility: 1-min ATR as % of price: best when **0.5 or more** (7 trades, 29% winners, avg -0.013 USD), worst when **0.3 to 0.5** (20 trades, 15% winners, avg -0.069 USD)
* Market (SPY) since the open, %: best when **-0.3 to 0** (5 trades, 20% winners, avg -0.034 USD), worst when **0 to 0.3** (10 trades, 20% winners, avg -0.065 USD)
* Costs as % of the trade: best when **0.5 to 0.75** (18 trades, 17% winners, avg -0.052 USD), worst when **0.3 to 0.5** (8 trades, 25% winners, avg -0.061 USD)
* Share price, USD: best when **5 to 8** (8 trades, 25% winners, avg -0.031 USD), worst when **8 to 12** (6 trades, 0% winners, avg -0.120 USD)

<details><summary>Minutes after the open</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 15 | 3 | 33 | -0.0450 | -0.1350 | -0.17 |
| 15 to 30 | 4 | 25 | -0.0281 | -0.1125 | +0.08 |
| 30 to 45 | 5 | 0 | -0.0787 | -0.3937 | -0.50 |
| 45 to 60 | 12 | 17 | -0.0613 | -0.7352 | -0.32 |
| 60 to 90 | 4 | 25 | -0.0534 | -0.2137 | -0.25 |

</details>

<details><summary>Stock's gain since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 1 | 6 | 17 | -0.0684 | -0.4107 | -0.24 |
| 1 to 2 | 4 | 25 | -0.0236 | -0.0944 | +0.11 |
| 3 to 5 | 14 | 14 | -0.0616 | -0.8629 | -0.29 |
| 5 or more | 4 | 25 | -0.0555 | -0.2221 | -0.58 |

</details>

<details><summary>Volume vs normal (x)</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 1.5 to 2 | 8 | 25 | -0.0415 | -0.3318 | -0.11 |
| 2 to 3 | 13 | 15 | -0.0701 | -0.9110 | -0.49 |
| 3 to 5 | 4 | 0 | -0.0930 | -0.3721 | -0.52 |
| 5 or more | 3 | 33 | +0.0083 | +0.0248 | +0.65 |

</details>

<details><summary>Price above VWAP, in ATRs</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 1 | 3 | 33 | -0.0252 | -0.0757 | -0.02 |
| 1 to 2 | 4 | 25 | -0.0197 | -0.0789 | +0.25 |
| 2 to 3 | 3 | 0 | -0.0671 | -0.2013 | -0.33 |
| 3 or more | 18 | 17 | -0.0686 | -1.2341 | -0.41 |

</details>

<details><summary>Volatility: 1-min ATR as % of price</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.2 to 0.3 | 1 | 0 | -0.1138 | -0.1138 | -0.81 |
| 0.3 to 0.5 | 20 | 15 | -0.0693 | -1.3853 | -0.34 |
| 0.5 or more | 7 | 29 | -0.0130 | -0.0909 | +0.03 |

</details>

<details><summary>Market (SPY) since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| -0.3 to 0 | 5 | 20 | -0.0339 | -0.1696 | +0.07 |
| 0 to 0.3 | 10 | 20 | -0.0646 | -0.6457 | -0.25 |
| 0.3 or more | 13 | 15 | -0.0596 | -0.7747 | -0.41 |

</details>

<details><summary>Costs as % of the trade</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.3 to 0.5 | 8 | 25 | -0.0614 | -0.4911 | -0.17 |
| 0.5 to 0.75 | 18 | 17 | -0.0516 | -0.9292 | -0.19 |
| 0.75 to 1 | 2 | 0 | -0.0848 | -0.1697 | -1.29 |

</details>

<details><summary>Share price, USD</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 3 | 3 | 67 | +0.0542 | +0.1625 | +1.31 |
| 3 to 5 | 11 | 9 | -0.0716 | -0.7873 | -0.49 |
| 5 to 8 | 8 | 25 | -0.0305 | -0.2442 | -0.06 |
| 8 to 12 | 6 | 0 | -0.1202 | -0.7210 | -0.92 |

</details>

## Current strategy replayed on all stored history

Strategy `{"name": "orb", "params": {"or_minutes": 5, "rvol_min": 2.0, "target_r": 2.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}}` over 21 trading days, updated by the weekly review. Larger sample, so patterns here are more reliable than in the real trades.

* Trades: 23; winners: 39.1%; total net after costs: +0.177 USD
* Average price move before costs: +0.65% per trade; average costs: 0.55% per trade
* How trades ended: stop 9, target 7, window_end 7

**What stands out** (groups of at least 5 trades):

* Minutes after the open: best when **0 to 15** (8 trades, 25% winners, avg +0.001 USD), worst when **30 to 45** (5 trades, 40% winners, avg +0.001 USD)
* Stock's gain since the open, %: best when **1 to 2** (11 trades, 64% winners, avg +0.074 USD), worst when **0 to 1** (12 trades, 17% winners, avg -0.053 USD)
* Volume vs normal (x): best when **2 to 3** (10 trades, 50% winners, avg +0.040 USD), worst when **3 to 5** (8 trades, 25% winners, avg -0.027 USD)
* Price above VWAP, in ATRs: best when **1 to 2** (6 trades, 50% winners, avg +0.057 USD), worst when **2 to 3** (5 trades, 40% winners, avg -0.014 USD)
* Volatility: 1-min ATR as % of price: best when **0.5 or more** (5 trades, 60% winners, avg +0.126 USD), worst when **0.3 to 0.5** (18 trades, 33% winners, avg -0.025 USD)
* Market (SPY) since the open, %: best when **0 to 0.3** (12 trades, 33% winners, avg +0.021 USD), worst when **0.3 or more** (9 trades, 44% winners, avg -0.002 USD)
* Costs as % of the trade: best when **0.3 to 0.5** (8 trades, 75% winners, avg +0.124 USD), worst when **0.5 to 0.75** (15 trades, 20% winners, avg -0.054 USD)
* Share price, USD: best when **5 to 8** (5 trades, 60% winners, avg +0.074 USD), worst when **0 to 3** (7 trades, 14% winners, avg -0.033 USD)

<details><summary>Minutes after the open</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 15 | 8 | 25 | +0.0014 | +0.0110 | +0.64 |
| 15 to 30 | 3 | 100 | +0.1039 | +0.3116 | +1.81 |
| 30 to 45 | 5 | 40 | +0.0011 | +0.0056 | +0.42 |
| 45 to 60 | 4 | 25 | -0.0299 | -0.1198 | +0.34 |
| 60 to 90 | 3 | 33 | -0.0105 | -0.0315 | +0.30 |

</details>

<details><summary>Stock's gain since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 1 | 12 | 17 | -0.0534 | -0.6404 | -0.08 |
| 1 to 2 | 11 | 64 | +0.0743 | +0.8173 | +1.44 |

</details>

<details><summary>Volume vs normal (x)</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 2 to 3 | 10 | 50 | +0.0404 | +0.4036 | +1.10 |
| 3 to 5 | 8 | 25 | -0.0268 | -0.2141 | +0.11 |
| 5 or more | 5 | 40 | -0.0025 | -0.0126 | +0.59 |

</details>

<details><summary>Price above VWAP, in ATRs</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 1 | 4 | 25 | -0.0179 | -0.0716 | +0.29 |
| 1 to 2 | 6 | 50 | +0.0569 | +0.3412 | +1.45 |
| 2 to 3 | 5 | 40 | -0.0139 | -0.0695 | +0.40 |
| 3 or more | 8 | 38 | -0.0029 | -0.0232 | +0.37 |

</details>

<details><summary>Volatility: 1-min ATR as % of price</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.3 to 0.5 | 18 | 33 | -0.0253 | -0.4546 | +0.26 |
| 0.5 or more | 5 | 60 | +0.1263 | +0.6315 | +2.05 |

</details>

<details><summary>Market (SPY) since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| -0.3 to 0 | 2 | 50 | -0.0286 | -0.0573 | +0.25 |
| 0 to 0.3 | 12 | 33 | +0.0213 | +0.2555 | +0.75 |
| 0.3 or more | 9 | 44 | -0.0024 | -0.0213 | +0.59 |

</details>

<details><summary>Costs as % of the trade</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.3 to 0.5 | 8 | 75 | +0.1243 | +0.9940 | +1.90 |
| 0.5 to 0.75 | 15 | 20 | -0.0545 | -0.8171 | -0.02 |

</details>

<details><summary>Share price, USD</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 3 | 7 | 14 | -0.0335 | -0.2345 | +0.28 |
| 3 to 5 | 7 | 43 | -0.0076 | -0.0529 | +0.38 |
| 5 to 8 | 5 | 60 | +0.0744 | +0.3721 | +1.49 |
| 8 to 12 | 4 | 50 | +0.0230 | +0.0921 | +0.70 |

</details>
