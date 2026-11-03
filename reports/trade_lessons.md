# Trade lessons

What winning and losing trades had in common at the moment of buying. Analysis only: a pattern becomes a rule only after it is added as a fixed strategy variant and passes the weekly walk-forward test.

## Real paper trades

All simulated trades so far, updated after every session.

* Trades: 21; winners: 23.8%; total net after costs: -0.956 USD
* Average price move before costs: -0.01% per trade; average costs: 0.54% per trade
* How trades ended: stop 12, window_end 7, target 2

**What stands out** (groups of at least 5 trades):

* Stock's gain since the open, %: best when **3 to 5** (9 trades, 22% winners, avg -0.044 USD), worst when **0 to 1** (6 trades, 17% winners, avg -0.068 USD)
* Volume vs normal (x): best when **1.5 to 2** (6 trades, 33% winners, avg -0.018 USD), worst when **2 to 3** (9 trades, 22% winners, avg -0.060 USD)
* Market (SPY) since the open, %: best when **0.3 or more** (6 trades, 33% winners, avg -0.023 USD), worst when **0 to 0.3** (10 trades, 20% winners, avg -0.065 USD)
* Costs as % of the trade: best when **0.5 to 0.75** (13 trades, 23% winners, avg -0.036 USD), worst when **0.3 to 0.5** (8 trades, 25% winners, avg -0.061 USD)
* Share price, USD: best when **5 to 8** (5 trades, 40% winners, avg +0.009 USD), worst when **8 to 12** (6 trades, 0% winners, avg -0.120 USD)

<details><summary>Minutes after the open</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 15 | 3 | 33 | -0.0450 | -0.1350 | -0.17 |
| 15 to 30 | 3 | 33 | -0.0158 | -0.0473 | +0.42 |
| 30 to 45 | 3 | 0 | -0.0633 | -0.1898 | -0.21 |
| 45 to 60 | 9 | 22 | -0.0528 | -0.4749 | -0.09 |
| 60 to 90 | 3 | 33 | -0.0364 | -0.1093 | +0.12 |

</details>

<details><summary>Stock's gain since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 1 | 6 | 17 | -0.0684 | -0.4107 | -0.24 |
| 1 to 2 | 4 | 25 | -0.0236 | -0.0944 | +0.11 |
| 3 to 5 | 9 | 22 | -0.0443 | -0.3987 | +0.04 |
| 5 or more | 2 | 50 | -0.0262 | -0.0524 | +0.13 |

</details>

<details><summary>Volume vs normal (x)</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 1.5 to 2 | 6 | 33 | -0.0180 | -0.1083 | +0.37 |
| 2 to 3 | 9 | 22 | -0.0597 | -0.5375 | -0.25 |
| 3 to 5 | 3 | 0 | -0.1118 | -0.3353 | -0.74 |
| 5 or more | 3 | 33 | +0.0083 | +0.0248 | +0.65 |

</details>

<details><summary>Price above VWAP, in ATRs</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 1 | 2 | 50 | +0.0143 | +0.0286 | +0.64 |
| 1 to 2 | 4 | 25 | -0.0197 | -0.0789 | +0.25 |
| 2 to 3 | 3 | 0 | -0.0671 | -0.2013 | -0.33 |
| 3 or more | 12 | 25 | -0.0587 | -0.7047 | -0.13 |

</details>

<details><summary>Volatility: 1-min ATR as % of price</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.2 to 0.3 | 1 | 0 | -0.1138 | -0.1138 | -0.81 |
| 0.3 to 0.5 | 16 | 19 | -0.0650 | -1.0403 | -0.23 |
| 0.5 or more | 4 | 50 | +0.0495 | +0.1979 | +1.06 |

</details>

<details><summary>Market (SPY) since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| -0.3 to 0 | 5 | 20 | -0.0339 | -0.1696 | +0.07 |
| 0 to 0.3 | 10 | 20 | -0.0646 | -0.6457 | -0.25 |
| 0.3 or more | 6 | 33 | -0.0235 | -0.1409 | +0.30 |

</details>

<details><summary>Costs as % of the trade</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.3 to 0.5 | 8 | 25 | -0.0614 | -0.4911 | -0.17 |
| 0.5 to 0.75 | 13 | 23 | -0.0358 | -0.4651 | +0.08 |

</details>

<details><summary>Share price, USD</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 3 | 3 | 67 | +0.0542 | +0.1625 | +1.31 |
| 3 to 5 | 7 | 14 | -0.0634 | -0.4441 | -0.23 |
| 5 to 8 | 5 | 40 | +0.0093 | +0.0464 | +0.57 |
| 8 to 12 | 6 | 0 | -0.1202 | -0.7210 | -0.92 |

</details>

## Current strategy replayed on all stored history

Strategy `{"name": "momentum_leaders", "params": {"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 4.0, "take_profit": 0.03, "first_minute": 15, "last_entry_minute": 75}}` over 21 trading days, updated by the weekly review. Larger sample, so patterns here are more reliable than in the real trades.

* Trades: 27; winners: 37.0%; total net after costs: -0.436 USD
* Average price move before costs: +0.36% per trade; average costs: 0.56% per trade
* How trades ended: stop 16, window_end 7, target 4

**What stands out** (groups of at least 5 trades):

* Minutes after the open: best when **60 to 90** (7 trades, 29% winners, avg -0.031 USD), worst when **45 to 60** (8 trades, 25% winners, avg -0.067 USD)
* Volume vs normal (x): best when **1.5 to 2** (14 trades, 36% winners, avg -0.002 USD), worst when **2 to 3** (5 trades, 20% winners, avg -0.082 USD)
* Market (SPY) since the open, %: best when **0.3 or more** (6 trades, 50% winners, avg +0.050 USD), worst when **-0.3 to 0** (9 trades, 11% winners, avg -0.064 USD)
* Costs as % of the trade: best when **0.3 to 0.5** (8 trades, 62% winners, avg +0.038 USD), worst when **0.5 to 0.75** (18 trades, 28% winners, avg -0.033 USD)
* Share price, USD: best when **5 to 8** (10 trades, 40% winners, avg +0.005 USD), worst when **3 to 5** (9 trades, 22% winners, avg -0.046 USD)

<details><summary>Minutes after the open</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 15 to 30 | 8 | 38 | -0.0341 | -0.2725 | +0.03 |
| 30 to 45 | 4 | 75 | +0.1468 | +0.5871 | +2.39 |
| 45 to 60 | 8 | 25 | -0.0668 | -0.5345 | -0.11 |
| 60 to 90 | 7 | 29 | -0.0309 | -0.2160 | +0.14 |

</details>

<details><summary>Stock's gain since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 3 to 5 | 26 | 35 | -0.0237 | -0.6154 | +0.26 |
| 5 or more | 1 | 100 | +0.1794 | +0.1794 | +3.15 |

</details>

<details><summary>Volume vs normal (x)</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 1.5 to 2 | 14 | 36 | -0.0017 | -0.0240 | +0.48 |
| 2 to 3 | 5 | 20 | -0.0822 | -0.4109 | -0.47 |
| 3 to 5 | 4 | 25 | -0.0855 | -0.3419 | -0.42 |
| 5 or more | 4 | 75 | +0.0852 | +0.3409 | +1.81 |

</details>

<details><summary>Price above VWAP, in ATRs</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 2 to 3 | 4 | 25 | -0.0333 | -0.1332 | -0.13 |
| 3 or more | 23 | 39 | -0.0132 | -0.3028 | +0.45 |

</details>

<details><summary>Volatility: 1-min ATR as % of price</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.2 to 0.3 | 3 | 33 | -0.0504 | -0.1511 | -0.20 |
| 0.3 to 0.5 | 21 | 33 | -0.0212 | -0.4446 | +0.31 |
| 0.5 or more | 3 | 67 | +0.0533 | +0.1598 | +1.34 |

</details>

<details><summary>Market (SPY) since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| -0.3 to 0 | 9 | 11 | -0.0642 | -0.5776 | -0.33 |
| 0 to 0.3 | 12 | 50 | -0.0133 | -0.1598 | +0.47 |
| 0.3 or more | 6 | 50 | +0.0502 | +0.3014 | +1.20 |

</details>

<details><summary>Costs as % of the trade</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.3 to 0.5 | 8 | 62 | +0.0379 | +0.3035 | +1.01 |
| 0.5 to 0.75 | 18 | 28 | -0.0334 | -0.6003 | +0.21 |
| 0.75 to 1 | 1 | 0 | -0.1392 | -0.1392 | -1.99 |

</details>

<details><summary>Share price, USD</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 3 | 2 | 50 | +0.0006 | +0.0011 | +0.46 |
| 3 to 5 | 9 | 22 | -0.0459 | -0.4134 | +0.13 |
| 5 to 8 | 10 | 40 | +0.0047 | +0.0474 | +0.59 |
| 8 to 12 | 6 | 50 | -0.0119 | -0.0711 | +0.32 |

</details>
