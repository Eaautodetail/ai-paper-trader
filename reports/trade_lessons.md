# Trade lessons

What winning and losing trades had in common at the moment of buying. Analysis only: a pattern becomes a rule only after it is added as a fixed strategy variant and passes the weekly walk-forward test.

## Real paper trades

All simulated trades so far, updated after every session.

* Trades: 11; winners: 18.2%; total net after costs: -0.633 USD
* Average price move before costs: -0.18% per trade; average costs: 0.55% per trade
* How trades ended: stop 7, window_end 3, target 1

_Too few trades per group (needs 5) to call out patterns yet._

<details><summary>Minutes after the open</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 15 | 3 | 33 | -0.0450 | -0.1350 | -0.17 |
| 15 to 30 | 2 | 0 | -0.1115 | -0.2230 | -0.86 |
| 30 to 45 | 2 | 0 | -0.0901 | -0.1802 | -0.53 |
| 45 to 60 | 4 | 25 | -0.0237 | -0.0947 | +0.32 |

</details>

<details><summary>Stock's gain since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 1 | 6 | 17 | -0.0684 | -0.4107 | -0.24 |
| 1 to 2 | 4 | 25 | -0.0236 | -0.0944 | +0.11 |
| 3 to 5 | 1 | 0 | -0.1277 | -0.1277 | -1.03 |

</details>

<details><summary>Volume vs normal (x)</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 2 to 3 | 5 | 20 | -0.0645 | -0.3224 | -0.35 |
| 3 to 5 | 3 | 0 | -0.1118 | -0.3353 | -0.74 |
| 5 or more | 3 | 33 | +0.0083 | +0.0248 | +0.65 |

</details>

<details><summary>Price above VWAP, in ATRs</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 1 | 2 | 50 | +0.0143 | +0.0286 | +0.64 |
| 1 to 2 | 4 | 25 | -0.0197 | -0.0789 | +0.25 |
| 2 to 3 | 1 | 0 | -0.1119 | -0.1119 | -0.90 |
| 3 or more | 4 | 0 | -0.1177 | -0.4706 | -0.84 |

</details>

<details><summary>Volatility: 1-min ATR as % of price</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.3 to 0.5 | 9 | 11 | -0.0846 | -0.7614 | -0.46 |
| 0.5 or more | 2 | 50 | +0.0643 | +0.1286 | +1.09 |

</details>

<details><summary>Market (SPY) since the open, %</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| -0.3 to 0 | 3 | 33 | -0.0330 | -0.0991 | +0.09 |
| 0 to 0.3 | 5 | 0 | -0.1134 | -0.5668 | -0.92 |
| 0.3 or more | 3 | 33 | +0.0110 | +0.0331 | +0.78 |

</details>

<details><summary>Costs as % of the trade</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0.3 to 0.5 | 3 | 0 | -0.1090 | -0.3269 | -0.80 |
| 0.5 to 0.75 | 8 | 25 | -0.0382 | -0.3059 | +0.05 |

</details>

<details><summary>Share price, USD</summary>

| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |
|---|---|---|---|---|---|
| 0 to 3 | 2 | 50 | +0.0580 | +0.1161 | +1.35 |
| 3 to 5 | 4 | 25 | -0.0749 | -0.2995 | -0.33 |
| 5 to 8 | 2 | 0 | -0.0613 | -0.1226 | -0.49 |
| 8 to 12 | 3 | 0 | -0.1090 | -0.3269 | -0.80 |

</details>

## Current strategy replayed on all stored history

Strategy `null` over 0 trading days, updated by the weekly review. Larger sample, so patterns here are more reliable than in the real trades.

No trades with stored bars yet.
