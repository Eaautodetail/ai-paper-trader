# AI paper trader (simulated only)

A self-running **paper-trading** agent for US stocks. It starts with **500 SEK of virtual money**,
trades only during the **first two hours of the New York session (09:30-11:30 New York time)** on real
NYSE trading days, records everything in a ledger, and stops by itself after a **three-session evaluation**.

> **Real-money trading is impossible in this version.** The program contains no brokerage connection,
> no order API and no account keys. `papertrader/safety.py` hard-codes `LIVE_TRADING_ENABLED = False`,
> the program refuses to start unless `config.toml` says `paper_trading = true`, and an automated test
> fails if any brokerage library or order endpoint ever appears in the code.

* Current status: **[STATUS.md](STATUS.md)**
* Session reports: [reports/evaluation/](reports/evaluation/) (one file per session)
* Final report after session 3: `reports/evaluation_final.md`
* Strategy backtest: [reports/backtest.md](reports/backtest.md)

---

## 1. What was chosen, and why

| Part | Choice | Why |
|---|---|---|
| Runs on | **GitHub Actions** in this repository | Free (this private repo gets GitHub's free monthly minutes; the evaluation uses roughly 8-9 hours). Runs on GitHub's servers, so your computer and browser can be off. No credit card. |
| Scheduler | GitHub Actions `schedule` + the **NYSE calendar** inside the program | GitHub wakes the program several times around the open; the program itself checks holidays, early closes and daylight saving. |
| Market data | **Yahoo Finance** via the open-source `yfinance` library (Apache-2.0) | Free, no account or key, 1-minute bars for US stocks, verified working from GitHub's servers. It is unofficial (no guarantee), so every session checks the data is current and skips safely if not. |
| Exchange calendar | `exchange_calendars` (Apache-2.0) | Official NYSE holidays and early closes. |
| Simulator ("broker") | **Built into this project** | Lets us model what matters for 500 SEK exactly: whole shares, USD/SEK, spreads, slippage and US fees. No outside account. |
| Ledger | SQLite file in `ledger/`, saved to GitHub after every change | Survives restarts; every order has a unique key so nothing is ever placed twice. |

**Options considered and not used:**

* *Alpaca paper trading / free IEX data*: good and free, but needs an account and secret keys, and its USD paper account does not model a 500 SEK account with currency conversion. Kept as a possible later upgrade for data.
* *Interactive Brokers paper account*: requires opening a full brokerage account first.
* *QuantConnect (LEAN), Backtrader, vectorbt, Zipline*: capable engines, but they are hosted with limits, partly no longer actively maintained, or heavy for a 500 SEK whole-share simulation. Our small engine uses the same code for backtest and live, which is easier to verify.
* *Polygon, Alpha Vantage, Finnhub, Tiingo free tiers*: free plans are delayed, end-of-day or have very low request limits for 1-minute data.
* *Oracle Cloud / Google Cloud free servers*: need a credit card to sign up, so not activated. *PythonAnywhere / Render / Railway free plans*: no reliable always-on or scheduled process on the free plan.
* *Your own computer* (alternative): works too (see section 8), but must be on and awake at 15:30 Swedish time.

## 2. How a trading day works

1. On weekdays GitHub starts the program a few times around 09:30 New York time and again after 11:30.
2. The program checks: Is today a NYSE trading day? Is the evaluation started? Is this session already done? If not needed, it exits within a minute.
3. It waits until 09:30 New York, then checks that the exchange actually opened and the data is current (latest SPY bar no more than 3 minutes old). If that fails by 09:45, **the session is skipped safely**, an alert is posted, and it does not count.
4. It picks today's stocks: liquid US stocks (over 20 million USD traded per day) priced so that at least one whole share fits within 20% of equity (with ~50 USD of equity, that means shares under about 10 USD).
5. Every ~20 seconds it reads the latest completed 1-minute bars, computes VWAP, momentum, volume, volatility (ATR) and trend, and the **strategy** may propose a trade.
6. The **risk manager** (separate code) approves or rejects each proposal and decides the number of whole shares.
7. At **11:30 New York** it stops opening trades, cancels pending orders and sells everything. Nothing is held overnight.
8. It writes a session report, updates STATUS.md, and saves everything to GitHub.

All times are calculated in New York time; reports show Stockholm time too. Both countries' daylight-saving changes are automatic. (Example: from 25 Oct to 1 Nov 2026 Sweden has already changed but the US has not, so the window is 14:30-16:30 in Stockholm that week, otherwise 15:30-17:30.)

## 3. Safety limits (enforced in code, not in a prompt)

| Rule | Where |
|---|---|
| One position at most **20% of current equity** | `risk.py`, and re-checked at the fill price in `engine.py` |
| Planned loss per trade (entry to stop, incl. costs) at most **0.5% of equity** | `risk.py` |
| Daily loss limit **2% of the session's starting equity**: stop trading and close everything | `engine.py` |
| Long only. No short selling, margin, leverage, options or derivatives | `risk.py`, `ledger.py` (selling more than you own is impossible) |
| Whole shares only; cash must cover the full purchase | `risk.py`, `ledger.py` |
| No new trades before 09:30 or from 11:30 New York; all closed at 11:30 | `engine.py` |
| Expected gain must be at least 2x the modeled costs | `risk.py` |
| Max 3 open positions, 6 entries and one entry per stock per session | `risk.py` |
| Limits cannot be loosened beyond 20% / 0.5% / 2% (the program refuses to start) | `risk.py` |

## 4. Costs and execution model

* 500 SEK are converted to USD once at the first session (0.25% conversion fee, like a USD account at a Swedish broker). Results are shown in USD and SEK.
* Orders are market orders filled at the **open of the next 1-minute bar**, plus half the bid/ask spread (0.05%, at least half a cent) plus 0.05% slippage.
* Stops fill at the stop or worse (if the price gaps). If a stop and a target are hit in the same minute, the stop is assumed (pessimistic).
* Commission: 0 (commission-free broker profile). US fees on every sale: SEC fee (20.60 USD per million) and FINRA fee, each rounded **up** to the next cent. With positions of about 10 USD these cents matter, and the reports show them.
* All of this can be changed in `config.toml` under `[costs]`.

## 5. Strategies, AI and backtesting

* Candidates (all deterministic, long only): **opening-range breakout**, **VWAP trend pullback**, **VWAP mean reversion**, plus a **do-nothing baseline**, in 22 variants.
* `Research -> backtest` replays recent real 1-minute data (Yahoo keeps about 30 days) through the *same* engine, risk limits and costs. The earlier two-thirds of the days choose the strategy (in-sample); the last third is only reported (out-of-sample).
* The chosen strategy is stored in `strategy/selected.json` and **frozen** for the whole evaluation.
* "AI" here means automated, measurable strategy research: candidates are generated, tested and ranked by the program with fixed rules. No language model makes or changes trading decisions, and the program cannot edit its own code, remove limits or enable real trading. A language-model commentary was not added because every useful option needs a paid API key.
* A few weeks of data is a small sample. **Nothing here shows a profitable edge**; see reports/backtest.md for the actual numbers.

## 6. Step-by-step: start, monitor, stop

You only need a web browser. Everything happens on github.com.

**Open the project**

1. Go to <https://github.com/Eaautodetail/ai-paper-trader> and sign in.
2. Click the **Actions** tab (top of the page). If GitHub asks, click **"I understand my workflows, go ahead and enable them"**.

**Get alerts by email (once)**

3. On the repository page, click **Watch** (top right) -> **Custom** -> tick **Issues** -> **Apply**. Alerts (skipped sessions, errors) arrive as GitHub issues, so you get an email.

**Start the 3-session evaluation**

4. Click **Actions** -> in the left list click **Control** -> click the **Run workflow** button (right side) -> choose **start-evaluation** -> click the green **Run workflow**.
5. After about a minute, a green tick appears. Open **STATUS.md** on the main page: it should say `Evaluation: RUNNING - 0/3 evaluation sessions completed` and show the next trading window in Stockholm time.
6. Nothing else is needed. The next three eligible US sessions run by themselves.

**Monitor**

7. **STATUS.md** shows mode (always PAPER), sessions done, equity in USD and SEK, and open positions.
8. During a session: **Actions -> Paper trading** shows a yellow (running) dot. Click it, then **session**, to see the live log. Grey "cancelled" runs are normal: GitHub starts spare runs as a backup and drops them when one is already running.
9. After each session: `reports/evaluation/<date>.md` lists every trade, cost, rejected signal and warning.

**Stop immediately**

10. **Actions -> Control -> Run workflow -> stop-now -> Run workflow.** A running session sees this within about a minute, sells all simulated positions at the next bar and ends. No new sessions start until you choose start-evaluation again.
11. Emergency stop (also blocks all future runs): **Actions -> Paper trading** (left list) -> the **...** button at the top right -> **Disable workflow**. If a run is in progress, open it and click **Cancel workflow run**. Any simulated position left open is closed at the 11:30 price the next time the workflow runs (after you re-enable it).

**Read the results**

12. After the third session the program writes **reports/evaluation_final.md**: starting and final value in USD and SEK, every session, number of trades, winners/losers, total costs and notes.

**Training after the evaluation (on by default)**

13. After the 3 sessions the same paper account keeps trading as **training** every trading day if this repository is public (unlimited free GitHub minutes), or only Tuesdays and Thursdays if it is private (to stay inside the ~33 free hours a month). It checks this by itself each run; the lists are `weekdays_public` and `weekdays` in `config.toml` -> `[training]` (0 = Monday ... 4 = Friday). STATUS.md says `TRAINING`. Daily reports go to `reports/training/<date>.md`. Set `enabled = false` there to stop after the evaluation instead.
14. Every Saturday, **Research -> weekly-review** re-tests all strategies on all real data collected so far (`data/bars/` grows each session). It switches strategy only if another one clearly did better on both older and recent days. Each decision is written to `reports/weekly_review.md` and `reports/learning_log.md`.
15. **reports/readiness.md** checks fixed rules after every session (at least 60 sessions and 100 trades, profitable over the last 40 sessions, statistically positive average per trade, profit factor at least 1.3, drawdown at most 10%, at least 2 of the last 3 twenty-session blocks positive, and the same strategy for at least 40 sessions). Only when all pass does it open the issue **"Agent self-check: ready for your review"**. It never switches to real money; that would be a separate project you decide on.

**Strategy lab**

16. Besides the main account, up to 8 *lab* accounts trade the same sessions, each with its own 500 SEK of play money and its own strategy (listed in `strategy/lab.json`). Same costs, limits and 11:30 deadline; they never affect the main account or its readiness check. The leaderboard is `reports/lab.md`.
17. A lab account is judged only after 20 sessions and 15 trades. It is retired (stops trading, record kept) if it is losing with a profit factor below 0.8, or if it is still losing after 40 sessions. Winners keep going.
18. Every week new ideas are added to the lab as rule sets (no code changes); **Research -> lab-backtest** tests all lab strategies on the stored history.

## 7. Useful extras

* **Actions -> Research -> check-data**: tests the data feed and exchange calendar right now.
* **Actions -> Research -> backtest**: re-runs the strategy comparison and updates reports/backtest.md (does not change a running evaluation).
* **Actions -> Research -> weekly-review**: runs the Saturday learning step now.
* **Actions -> Control -> rehearsal-next-session**: a full test session on a *separate* ledger (`ledger/rehearsal.sqlite`, `reports/rehearsal/`). It does not touch the evaluation.
* **Actions -> Tests**: runs the automated tests.

## 8. Alternative: run it on your own computer

Only needed if GitHub Actions is ever unavailable. Install Python 3.12 from python.org, download this repository (green **Code** button -> **Download ZIP**, unzip), open a terminal in the folder and run:

```
pip install -r requirements.txt
python -m papertrader start
python -m papertrader run-session
```

Keep the computer awake from 15:20 until about 17:45 Swedish time. On Windows you can schedule the last command with Task Scheduler for weekdays at 15:15 (and 14:15 in the late-October/March weeks when only one country has changed clocks).

## 9. Files

```
config.toml              all settings (capital, window, limits, costs, stock list)
papertrader/safety.py     hard paper-only switch
papertrader/market_calendar.py  NYSE calendar, time zones, daylight saving
papertrader/data.py       Yahoo data, USD/SEK, stock selection
papertrader/features.py   VWAP, EMA, ATR, RSI, momentum, volume, opening range
papertrader/strategies.py candidate strategies
papertrader/risk.py       independent risk manager
papertrader/costs.py      spread, slippage, fees; execution model
papertrader/engine.py     simulated broker + session engine (same code for backtest and live)
papertrader/ledger.py     persistent ledger (SQLite)
papertrader/live.py       scheduled session runner, recovery, skip logic
papertrader/backtest.py   in-sample / out-of-sample comparison
papertrader/report.py     session, status and final reports
.github/workflows/        trade.yml (schedule), control.yml (start/stop), research.yml, tests.yml
tests/                    automated tests (synthetic test data only)
```
