# Trade lessons

What winning and losing trades had in common at the moment of buying. Analysis only: a pattern becomes a rule only after it is added as a fixed strategy variant and passes the weekly walk-forward test.

## Real paper trades

All simulated trades so far, updated after every session.

* Trades: 33; winners: 15.2%; total net after costs: -2.156 USD
* Average price move before costs: -0.39% per trade; average costs: 0.59% per trade
* How trades ended: stop 23, window_end 8, target 2

**What stands out** (groups of at least 5 trades):

* Minutes after the open: best when **45 to 60** (12 trades, 17% winners, avg -0.061 USD), worst when **30 to 45** (6 trades, 0% winners, avg -0.088 USD)
* Stock's gain since the open, %: best when **1 to 2** (5 trades, 20% winners, avg -0.036 USD), worst when **0 to 1** (8 trades, 12% winners, avg -0.076 USD)
* Volume vs normal (x): best when **1.5 to 2** (8 trades, 25% winners, avg -0.041 USD), worst when **3 to 5** (5 trades, 0% winners, avg -0.104 USD)
* Price above VWAP, in ATRs: best when **1 to 2** (7 trades, 14% winners, avg -0.061 USD), worst when **3 or more** (19 trades, 16% winners, avg -0.069 USD)
* Volatility: 1-min ATR as % of price: best when **0.5 or more** (9 trades, 22% winners, avg -0.042 USD), worst when **0.3 to 0.5** (23 trades, 13% winners, avg -0.072 USD)
* Market (SPY) since the open, %: best when **-0.3 to 0** (5 trades, 20% winners, avg -0.034 USD), worst when **0 to 0.3** (12 trades, 17% winners, avg -0.073 USD)
* Costs as % of the trade: best when **0.3 to 0.5** (8 trades, 25% winners, avg -0.061 USD), worst when **0.5 to 0.75** (23 trades, 13% winners, avg -0.065 USD)
* Share price, USD: best when **5 to 8** (11 trades, 18% winners, avg -0.051 USD), worst when **8 to 12** (6 trades, 0% winners, avg -0.120 USD)

<details><summary>Minutes after the open</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 15 | 3 | 33 | -0.0450 | -0.1350 | -0.17 |
| 15 to 30 | 7 | 14 | -0.0616 | -0.4315 | -0.46 |
| 30 to 45 | 6 | 0 | -0.0883 | -0.5298 | -0.59 |
| 45 to 60 | 12 | 17 | -0.0613 | -0.7352 | -0.32 |
| 60 to 90 | 5 | 20 | -0.0649 | -0.3245 | -0.38 |

</details>

<details><summary>Stock's gain since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 1 | 8 | 12 | -0.0755 | -0.6041 | -0.40 |
| 1 to 2 | 5 | 20 | -0.0363 | -0.1816 | -0.11 |
| 2 to 3 | 1 | 0 | -0.1361 | -0.1361 | -1.07 |
| 3 to 5 | 15 | 13 | -0.0675 | -1.0120 | -0.38 |
| 5 or more | 4 | 25 | -0.0555 | -0.2221 | -0.58 |

</details>

<details><summary>Volume vs normal (x)</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 1.5 to 2 | 8 | 25 | -0.0415 | -0.3318 | -0.11 |
| 2 to 3 | 16 | 12 | -0.0761 | -1.2170 | -0.59 |
| 3 to 5 | 5 | 0 | -0.1042 | -0.5212 | -0.74 |
| 5 or more | 4 | 25 | -0.0215 | -0.0860 | +0.26 |

</details>

<details><summary>Price above VWAP, in ATRs</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 1 | 3 | 33 | -0.0252 | -0.0757 | -0.02 |
| 1 to 2 | 7 | 14 | -0.0609 | -0.4262 | -0.37 |
| 2 to 3 | 4 | 0 | -0.0844 | -0.3374 | -0.52 |
| 3 or more | 19 | 16 | -0.0693 | -1.3167 | -0.44 |

</details>

<details><summary>Volatility: 1-min ATR as % of price</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.2 to 0.3 | 1 | 0 | -0.1138 | -0.1138 | -0.81 |
| 0.3 to 0.5 | 23 | 13 | -0.0724 | -1.6660 | -0.42 |
| 0.5 or more | 9 | 22 | -0.0418 | -0.3762 | -0.28 |

</details>

<details><summary>Market (SPY) since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| -0.3 to 0 | 5 | 20 | -0.0339 | -0.1696 | +0.07 |
| 0 to 0.3 | 12 | 17 | -0.0731 | -0.8774 | -0.42 |
| 0.3 or more | 16 | 12 | -0.0693 | -1.1089 | -0.52 |

</details>

<details><summary>Costs as % of the trade</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.3 to 0.5 | 8 | 25 | -0.0614 | -0.4911 | -0.17 |
| 0.5 to 0.75 | 23 | 13 | -0.0650 | -1.4952 | -0.39 |
| 0.75 to 1 | 2 | 0 | -0.0848 | -0.1697 | -1.29 |

</details>

<details><summary>Share price, USD</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 3 | 3 | 67 | +0.0542 | +0.1625 | +1.31 |
| 3 to 5 | 13 | 8 | -0.0796 | -1.0342 | -0.56 |
| 5 to 8 | 11 | 18 | -0.0512 | -0.5632 | -0.37 |
| 8 to 12 | 6 | 0 | -0.1202 | -0.7210 | -0.92 |

</details>

## Current strategy replayed on all stored history

Strategy `{"name": "orb", "params": {"or_minutes": 5, "rvol_min": 2.0, "target_r": 2.5, "stop_atr": 2.0, "last_entry_minute": 90, "market_filter": true}}` over 21 trading days, updated by the weekly review. Larger sample, so patterns here are more reliable than in the real trades.

* Trades: 23; winners: 34.8%; total net after costs: -0.069 USD
* Average price move before costs: +0.55% per trade; average costs: 0.56% per trade
* How trades ended: stop 11, target 7, window_end 5

**What stands out** (groups of at least 5 trades):

* Minutes after the open: best when **15 to 30** (7 trades, 57% winners, avg +0.048 USD), worst when **0 to 15** (5 trades, 20% winners, avg +0.009 USD)
* Stock's gain since the open, %: best when **1 to 2** (10 trades, 60% winners, avg +0.063 USD), worst when **0 to 1** (9 trades, 11% winners, avg -0.070 USD)
* Volume vs normal (x): best when **2 to 3** (12 trades, 42% winners, avg +0.034 USD), worst when **3 to 5** (5 trades, 20% winners, avg -0.071 USD)
* Price above VWAP, in ATRs: best when **1 to 2** (10 trades, 30% winners, avg -0.004 USD), worst when **2 to 3** (6 trades, 33% winners, avg -0.034 USD)
* Volatility: 1-min ATR as % of price: best when **0.5 or more** (7 trades, 43% winners, avg +0.066 USD), worst when **0.3 to 0.5** (16 trades, 31% winners, avg -0.033 USD)
* Market (SPY) since the open, %: best when **0.3 or more** (11 trades, 45% winners, avg +0.010 USD), worst when **0 to 0.3** (11 trades, 27% winners, avg -0.006 USD)
* Costs as % of the trade: best when **0.3 to 0.5** (7 trades, 86% winners, avg +0.148 USD), worst when **0.5 to 0.75** (16 trades, 12% winners, avg -0.069 USD)
* Share price, USD: best when **5 to 8** (8 trades, 50% winners, avg +0.061 USD), worst when **3 to 5** (7 trades, 14% winners, avg -0.072 USD)

<details><summary>Minutes after the open</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 15 | 5 | 20 | +0.0091 | +0.0456 | +0.81 |
| 15 to 30 | 7 | 57 | +0.0484 | +0.3386 | +1.12 |
| 30 to 45 | 4 | 25 | -0.0597 | -0.2388 | -0.18 |
| 45 to 60 | 4 | 25 | -0.0299 | -0.1198 | +0.34 |
| 60 to 90 | 3 | 33 | -0.0314 | -0.0943 | +0.04 |

</details>

<details><summary>Stock's gain since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 1 | 9 | 11 | -0.0702 | -0.6318 | -0.25 |
| 1 to 2 | 10 | 60 | +0.0626 | +0.6260 | +1.32 |
| 2 to 3 | 2 | 0 | -0.0866 | -0.1732 | -0.46 |
| 3 to 5 | 2 | 50 | +0.0551 | +0.1103 | +1.31 |

</details>

<details><summary>Volume vs normal (x)</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 2 to 3 | 12 | 42 | +0.0340 | +0.4077 | +1.04 |
| 3 to 5 | 5 | 20 | -0.0706 | -0.3530 | -0.39 |
| 5 or more | 6 | 33 | -0.0206 | -0.1235 | +0.34 |

</details>

<details><summary>Price above VWAP, in ATRs</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 1 | 1 | 100 | +0.2594 | +0.2594 | +4.26 |
| 1 to 2 | 10 | 30 | -0.0039 | -0.0388 | +0.54 |
| 2 to 3 | 6 | 33 | -0.0343 | -0.2057 | +0.15 |
| 3 or more | 6 | 33 | -0.0139 | -0.0837 | +0.34 |

</details>

<details><summary>Volatility: 1-min ATR as % of price</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.3 to 0.5 | 16 | 31 | -0.0331 | -0.5291 | +0.15 |
| 0.5 or more | 7 | 43 | +0.0658 | +0.4603 | +1.46 |

</details>

<details><summary>Market (SPY) since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| -0.3 to 0 | 1 | 0 | -0.1173 | -0.1173 | -0.71 |
| 0 to 0.3 | 11 | 27 | -0.0057 | -0.0628 | +0.47 |
| 0.3 or more | 11 | 45 | +0.0101 | +0.1113 | +0.74 |

</details>

<details><summary>Costs as % of the trade</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.3 to 0.5 | 7 | 86 | +0.1483 | +1.0379 | +2.37 |
| 0.5 to 0.75 | 16 | 12 | -0.0692 | -1.1067 | -0.25 |

</details>

<details><summary>Share price, USD</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 3 | 5 | 20 | -0.0386 | -0.1932 | +0.21 |
| 3 to 5 | 7 | 14 | -0.0722 | -0.5053 | -0.30 |
| 5 to 8 | 8 | 50 | +0.0612 | +0.4896 | +1.35 |
| 8 to 12 | 3 | 67 | +0.0467 | +0.1402 | +0.97 |

</details>
