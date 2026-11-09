# Trade lessons

What winning and losing trades had in common at the moment of buying. Analysis only: a pattern becomes a rule only after it is added as a fixed strategy variant and passes the weekly walk-forward test.

## Real paper trades

All simulated trades so far, updated after every session.

* Trades: 31; winners: 16.1%; total net after costs: -1.924 USD
* Average price move before costs: -0.34% per trade; average costs: 0.59% per trade
* How trades ended: stop 21, window_end 8, target 2

**What stands out** (groups of at least 5 trades):

* Minutes after the open: best when **15 to 30** (5 trades, 20% winners, avg -0.040 USD), worst when **30 to 45** (6 trades, 0% winners, avg -0.088 USD)
* Stock's gain since the open, %: best when **1 to 2** (5 trades, 20% winners, avg -0.036 USD), worst when **0 to 1** (7 trades, 14% winners, avg -0.075 USD)
* Volume vs normal (x): best when **1.5 to 2** (8 trades, 25% winners, avg -0.041 USD), worst when **2 to 3** (15 trades, 13% winners, avg -0.076 USD)
* Price above VWAP, in ATRs: best when **1 to 2** (6 trades, 17% winners, avg -0.046 USD), worst when **3 or more** (18 trades, 17% winners, avg -0.069 USD)
* Volatility: 1-min ATR as % of price: best when **0.5 or more** (8 trades, 25% winners, avg -0.028 USD), worst when **0.3 to 0.5** (22 trades, 14% winners, avg -0.072 USD)
* Market (SPY) since the open, %: best when **-0.3 to 0** (5 trades, 20% winners, avg -0.034 USD), worst when **0.3 or more** (16 trades, 12% winners, avg -0.069 USD)
* Costs as % of the trade: best when **0.5 to 0.75** (21 trades, 14% winners, avg -0.060 USD), worst when **0.3 to 0.5** (8 trades, 25% winners, avg -0.061 USD)
* Share price, USD: best when **5 to 8** (9 trades, 22% winners, avg -0.037 USD), worst when **8 to 12** (6 trades, 0% winners, avg -0.120 USD)

<details><summary>Minutes after the open</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 15 | 3 | 33 | -0.0450 | -0.1350 | -0.17 |
| 15 to 30 | 5 | 20 | -0.0400 | -0.1998 | -0.13 |
| 30 to 45 | 6 | 0 | -0.0883 | -0.5298 | -0.59 |
| 45 to 60 | 12 | 17 | -0.0613 | -0.7352 | -0.32 |
| 60 to 90 | 5 | 20 | -0.0649 | -0.3245 | -0.38 |

</details>

<details><summary>Stock's gain since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 1 | 7 | 14 | -0.0745 | -0.5215 | -0.33 |
| 1 to 2 | 5 | 20 | -0.0363 | -0.1816 | -0.11 |
| 2 to 3 | 1 | 0 | -0.1361 | -0.1361 | -1.07 |
| 3 to 5 | 14 | 14 | -0.0616 | -0.8629 | -0.29 |
| 5 or more | 4 | 25 | -0.0555 | -0.2221 | -0.58 |

</details>

<details><summary>Volume vs normal (x)</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 1.5 to 2 | 8 | 25 | -0.0415 | -0.3318 | -0.11 |
| 2 to 3 | 15 | 13 | -0.0756 | -1.1344 | -0.56 |
| 3 to 5 | 4 | 0 | -0.0930 | -0.3721 | -0.52 |
| 5 or more | 4 | 25 | -0.0215 | -0.0860 | +0.26 |

</details>

<details><summary>Price above VWAP, in ATRs</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 1 | 3 | 33 | -0.0252 | -0.0757 | -0.02 |
| 1 to 2 | 6 | 17 | -0.0462 | -0.2770 | -0.15 |
| 2 to 3 | 4 | 0 | -0.0844 | -0.3374 | -0.52 |
| 3 or more | 18 | 17 | -0.0686 | -1.2341 | -0.41 |

</details>

<details><summary>Volatility: 1-min ATR as % of price</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.2 to 0.3 | 1 | 0 | -0.1138 | -0.1138 | -0.81 |
| 0.3 to 0.5 | 22 | 14 | -0.0720 | -1.5834 | -0.40 |
| 0.5 or more | 8 | 25 | -0.0284 | -0.2270 | -0.11 |

</details>

<details><summary>Market (SPY) since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| -0.3 to 0 | 5 | 20 | -0.0339 | -0.1696 | +0.07 |
| 0 to 0.3 | 10 | 20 | -0.0646 | -0.6457 | -0.25 |
| 0.3 or more | 16 | 12 | -0.0693 | -1.1089 | -0.52 |

</details>

<details><summary>Costs as % of the trade</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.3 to 0.5 | 8 | 25 | -0.0614 | -0.4911 | -0.17 |
| 0.5 to 0.75 | 21 | 14 | -0.0602 | -1.2635 | -0.31 |
| 0.75 to 1 | 2 | 0 | -0.0848 | -0.1697 | -1.29 |

</details>

<details><summary>Share price, USD</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 3 | 3 | 67 | +0.0542 | +0.1625 | +1.31 |
| 3 to 5 | 13 | 8 | -0.0796 | -1.0342 | -0.56 |
| 5 to 8 | 9 | 22 | -0.0368 | -0.3315 | -0.17 |
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
