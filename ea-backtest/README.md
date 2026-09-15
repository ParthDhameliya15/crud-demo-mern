# XAUUSD 2-Candle Breakout EA — backtest tooling

`backtest_2candle.py` replicates the bar-by-bar logic of
`XAUUSD_2Candle_BuySellEA.mq5` (v1.40) so the strategy can be evaluated
outside MetaTrader. Pure Python 3, no third-party packages.

## 1. Get the bars

### Option A — pull them automatically (recommended)

On the Windows machine running MT5:

```bash
pip install MetaTrader5
python fetch_mt5_data.py --symbol XAUUSD --timeframe M5 --years 2
```

`fetch_mt5_data.py` connects to the running terminal, pulls the range in
monthly chunks (one huge request tends to hit terminal limits), de-duplicates
and writes `XAUUSD_M5.csv` in exactly the layout the backtester wants —
including the real per-bar spread column.

If the symbol name is wrong the script lists the gold symbols your broker
actually offers (`XAUUSD.m`, `GOLD`, `XAUUSDm` … all exist in the wild).
If you get far fewer bars than expected, open the chart, press Home, scroll
left to force MT5 to download history, then re-run.

### Option B — export by hand

In MetaTrader 5: open the XAUUSD chart on the timeframe you run the EA on →
**Tools → Options → Charts** → set *Max bars in chart* high → scroll the chart
fully left to load history → right-click the chart → **Save As** → CSV.

The exported layout is what the script expects:

```
<DATE>  <TIME>  <OPEN>  <HIGH>  <LOW>  <CLOSE>  <TICKVOL>  <VOL>  <SPREAD>
```

Tab, comma and semicolon separators all work, header row optional.

## 2. Run

```bash
python3 backtest_2candle.py XAUUSD_M5.csv \
    --tp 250 --max-c3 30 --lot 0.01 --spread 25 \
    --trades-csv trades.csv
```

Defaults mirror the EA's inputs. Useful flags:

| flag | meaning |
|---|---|
| `--tp` | TP distance in price (`InpTakeProfitUSD`) |
| `--max-c3` | Candle-3 size filter (`InpMaxC3Size`) |
| `--spread` | fixed spread in points; `--use-csv-spread` uses the per-bar column |
| `--commission` | USD per lot per side, added as a round turn |
| `--single-position` | mirror `InpAllowMultiplePos = false` |
| `--no-buy` / `--no-sell` | test one side in isolation |
| `--ambiguous sl\|tp` | how to resolve a bar that spans both SL and TP |
| `--trades-csv` | write the full trade-by-trade list |

## 3. What is modelled, and what is approximated

Modelled exactly:

- both entry patterns and their close-vs-high / close-vs-low conditions
- the Candle-3 size filter
- trigger = Candle-3 extreme ± offset; SL = the opposite Candle-3 extreme;
  TP = trigger ± TP distance
- a setup arms on a new bar and expires when that bar closes without a break
- one setup = one entry
- **no time exit** — a position runs until SL or TP, however long that takes
- bid/ask: BUY breaks on ask and exits on bid, SELL the mirror
- gap opens fill at the bar open rather than at the trigger

Approximated — these are the honest limits of OHLC data:

1. **Intrabar path is unknown.** When one bar's range covers both SL and TP,
   the outcome is assumed by `--ambiguous` (default `sl`, the pessimistic
   reading). Real ticks decide this; the assumption matters most on the entry
   bar and on fast bars.
2. **Fixed spread** unless `--use-csv-spread` is passed. Real gold spread
   widens hard at the open, at news, and at rollover — exactly when this EA
   triggers.
3. **No slippage, no requotes, no swap.** With the EA's multi-day holds, swap
   is a real cost this model omits.
4. **No broker stops-level rejection.** The EA skips an entry when the SL sits
   inside the broker's minimum stop distance; the backtest takes every entry.

Results are therefore optimistic relative to live trading. For an authoritative
answer use MT5's own Strategy Tester in **"Every tick based on real ticks"**
mode, which resolves 1 and 2 properly.

## 4. Verification

The engine was checked against two hand-computed fixtures:

- BUY: C3 high 2010.00 → entry 2010.01, SL 2003.00, TP 2260.01, exit TP, +$250.00
- SELL: C3 low 1994.00 → entry 1993.99, SL 1999.50, TP 1743.99, exit SL, −$5.51

Both matched to the cent.

## 5. Reading the output

Note the shape of this strategy before reading any profit number. TP is 250
price units; SL is the Candle-3 range, capped at 30 and usually far smaller. So
average win / average loss runs somewhere between 10:1 and 50:1, and the
break-even win rate is only about 1–3%. Two consequences:

- A **low win rate is expected and is not by itself a failure.** Compare the win
  rate against `gross profit / gross loss` instead.
- Because positions have no time exit, results depend heavily on the sample
  period. A gold bull market lets BUY trades reach +250 on multi-month holds;
  a ranging period does not. Test bull, bear and ranging stretches separately
  before drawing conclusions.
