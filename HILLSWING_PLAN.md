# HillSwing: 0–5 Day Swing Trading System — Implementation Plan

---

## Core Philosophy

Two setup types only. Never blend them.
- **Setup A — Momentum Continuation:** Stock broke out on volume, now pulling back quietly to an EMA. Enter on reclaim of the breakout level.
- **Setup B — Exhaustion Reversal:** Stock down 12–22% in 3–5 days on panic (not earnings), showing a capitulation candle. Enter at next day's open.

Market regime gates everything. No regime check = no trades run.

---

## Non-Negotiable Rules

1. Never enter on the spike day. Day 2 or Day 3 only.
2. Time stop: exit any position that hasn't moved 1R in your favor within 48 hours, no debate.
3. No earnings within 5 days. Hard kill.
4. Max 6 open positions. Max 2 per sector. Max 3% of portfolio per name.
5. Bear regime → no trades. Neutral regime → Setup B only, half size.

---

## Tech Stack

| Component | Tool |
|---|---|
| Orchestration | LangGraph (StateGraph) |
| LLM (deep) | Claude Sonnet (risk screener, trade brief) |
| LLM (quick) | Claude Haiku (regime summary, options context, portfolio summary) |
| Market data | Polygon.io Starter ($29/mo) — primary |
| Fallback data | yfinance — VIX, sector ETFs, earnings dates |
| Options flow | Polygon.io options or Unusual Whales ($50/mo) |
| Database | SQLite (`swingdb`) |
| Scheduler | APScheduler — runs at 6:00 PM ET daily |
| Alerts | Telegram Bot |
| Backtesting | vectorbt |

---

## Pipeline (6 Agents in sequence)

```
START
  ↓
Agent 0: Market Regime Classifier
  ↓ (bear → STOP)
Agent 1: Universe Builder
  ↓
Agent 2A: Momentum Scanner ──┐
Agent 2B: Reversal Scanner  ──┤ (parallel)
                              ↓
Agent 3: Options Flow Validator  (score < 4 → DROP)
                              ↓
Agent 4: Binary Risk Screener    (KILL verdict → DROP)
                              ↓
Agent 5: Trade Architect         (builds full trade plan)
                              ↓
Agent 6: Portfolio Gatekeeper    (concentration/correlation check)
                              ↓
OUTPUT: Final trade plans + Telegram alert
```

---

## Agent Summaries

**Agent 0 — Regime Classifier**
Rule-based scoring across: SPY vs 20/50/200-day MA, VIX level, VIX trend, breadth (% stocks above 20-day MA). Outputs `bull / neutral / bear`. No LLM for the decision — Haiku writes a 3-sentence narrative only.

**Agent 1 — Universe Builder**
Filters S&P 500 + Russell 1000 (~1,400 tickers) down to 50–150 candidates. Hard kills: ADV < 1.5M shares, price outside $10–$500, no options, earnings within 5 days, spread > 0.15%. Ranks survivors by 20-day relative strength vs SPY. No LLM.

**Agent 2A — Momentum Scanner**
All of these must be true: within 3% of 3-month high, had RVOL > 1.5x on breakout in last 3 days, now pulling back on RVOL < 0.8x (volume drying up), above both 8 and 21 EMA, RSI between 45–72, within 2% of either EMA. Entry trigger = yesterday's high. Stop = below yesterday's low or 21 EMA.

**Agent 2B — Reversal Scanner**
All of these must be true: down 12–22% over 3–5 days, no earnings in that window, RSI < 32, yesterday's candle closed in top 50% of its range on RVOL > 2x (capitulation), sector is not broadly collapsing, stock was above its 50-day MA before the drop. Entry = next day's open. Stop = below yesterday's low wick.

**Agent 3 — Options Flow Validator**
Scores 0–10 based on: net call vs put premium over 5 days, IV rank, put/call ratio trend, directional sweeps. Setup A wants call bias + low IV rank. Setup B wants call bias or put selling (not fresh put buying). Score < 4 → candidate dropped. Score 7+ → conviction +1. Haiku writes 2-sentence options context.

**Agent 4 — Binary Risk Screener**
Sonnet reviews last 48 hours of news + earnings calendar + recent SEC filings. Returns `CLEAR / CAUTION / KILL` in JSON. KILL → dropped. CAUTION → position size halved. Looks for: earnings, FDA decisions, merger votes, regulatory actions, SEC investigations.

**Agent 5 — Trade Architect**
Sizes position to risk exactly 1.5% of account per trade (capped at 3% position size). Sets Target 1 at 1.5R (sell 50% here, move stop to breakeven), Target 2 at 2.0–2.5R (trail the rest). Time stop date = 2 trading days from entry. Sonnet writes a structured trade brief: thesis, entry logic, invalidation, key risk, comparable setups.

**Agent 6 — Portfolio Gatekeeper**
Hard limits: max 6 positions total, max 2 per sector, max 20% total new exposure. Drops lower-conviction trades when slots are full. Rejects >2 reversal trades in non-bull regime. Haiku writes a 3-sentence portfolio risk summary.

---

## Entry & Exit Rules

**Entry:**
- Setup A: Stop-buy order placed at open of Day 2/3. Cancel if stock gaps up >3% (chasing).
- Setup B: Limit order at or below capitulation candle close. Reduce size 50% if gaps down >2% pre-market.

**Exit (priority order):**
1. Stop loss hit → exit immediately
2. Overnight news invalidates thesis → exit at open
3. Time stop (Day 3 open, <0.5R movement) → exit at open
4. Target 1 hit → sell 50%, move stop to breakeven
5. Target 2 hit or trailing stop → exit remainder

---

## File Structure

```
HillSwing/
├── swing/
│   ├── state.py
│   ├── graph.py
│   ├── agents/
│   │   ├── regime.py
│   │   ├── universe.py
│   │   ├── scanner_a.py
│   │   ├── scanner_b.py
│   │   ├── options.py
│   │   ├── risk.py
│   │   ├── architect.py
│   │   └── gatekeeper.py
│   ├── data/
│   │   ├── polygon.py
│   │   ├── yfinance_client.py
│   │   ├── options_flow.py
│   │   └── universe_list.py
│   ├── notify.py
│   ├── database.py
│   └── scheduler.py
├── swing_runner.py
└── backtests/
    ├── backtest_a.py
    └── backtest_b.py
```

---

## Implementation Order

| Week | Focus | Milestone |
|---|---|---|
| 1 | Data layer | Polygon + yfinance clients working, schema created |
| 2 | Agents 0–2 | Regime + universe + both scanners running on historical data |
| 3 | Agents 3–6 | Options, risk, architect, gatekeeper complete |
| 4 | Graph + delivery | Full pipeline wired, Telegram alerts live, scheduler running |
| 5 | Backtesting | 2 years of data tested; thresholds tuned if needed |
| 6 | Paper trading | 4 weeks of daily paper runs, results logged |
| 7+ | Go live | Only after paper avg R > 0 across minimum 20 trades |

---

## Expected Performance (Realistic)

| | Setup A | Setup B |
|---|---|---|
| Win rate | 48–55% | 42–50% |
| Avg R on winners | 1.8–2.2R | 1.4–1.7R |
| Avg R on losers | -1.0R | -1.0R |
| Expectancy | +0.4–0.7R/trade | +0.2–0.5R/trade |
| Works best in | Bull regime | Neutral / Bull |
| Avoid entirely | Bear regime | Bear regime |
