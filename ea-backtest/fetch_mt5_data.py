#!/usr/bin/env python3
"""
Pull XAUUSD history straight out of a running MetaTrader 5 terminal and write
it in the format backtest_2candle.py expects.

Run this on the Windows machine where MT5 is installed:

    pip install MetaTrader5
    python fetch_mt5_data.py --symbol XAUUSD --timeframe M5 --years 2

Writes e.g. XAUUSD_M5.csv, then:

    python backtest_2candle.py XAUUSD_M5.csv --trades-csv trades.csv

Notes
-----
* The MetaTrader5 package is Windows-only and needs the terminal running and
  logged in to the account whose history you want.
* MT5 only returns bars it has actually downloaded. If you get far fewer bars
  than expected, open the symbol's chart, press Home and scroll left to force
  the terminal to pull history, then re-run. Raising Tools -> Options ->
  Charts -> "Max bars in chart" helps too.
* Bar times are broker server time, not your local time. That is what you want
  for a backtest, since the EA sees the same clock.
"""

import argparse
import csv
import sys
from datetime import datetime, timedelta, timezone

try:
    import MetaTrader5 as mt5
except ImportError:
    sys.exit("MetaTrader5 package not found.  pip install MetaTrader5\n"
             "(Windows only, and the MT5 terminal must be running.)")

TIMEFRAMES = {
    "M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5, "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30, "H1": mt5.TIMEFRAME_H1, "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1,
}


def fail(msg):
    mt5.shutdown()
    sys.exit("error: %s  (MT5 said: %s)" % (msg, mt5.last_error()))


def fetch(symbol, tf, start, end, chunk_days):
    """Pull the range in chunks — one huge request often hits terminal limits."""
    seen, out = set(), []
    cursor = start
    while cursor < end:
        stop = min(cursor + timedelta(days=chunk_days), end)
        rates = mt5.copy_rates_range(symbol, tf, cursor, stop)
        if rates is not None and len(rates):
            for r in rates:
                if r["time"] not in seen:
                    seen.add(r["time"])
                    out.append(r)
            print("  %s -> %s : %d bars (total %d)"
                  % (cursor.date(), stop.date(), len(rates), len(out)))
        else:
            print("  %s -> %s : no data" % (cursor.date(), stop.date()))
        cursor = stop
    out.sort(key=lambda r: r["time"])
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--symbol", default="XAUUSD",
                   help="exact symbol name as your broker spells it "
                        "(XAUUSD.m, GOLD, XAUUSDm ... vary by broker)")
    p.add_argument("--timeframe", default="M5", choices=sorted(TIMEFRAMES))
    p.add_argument("--years", type=float, default=2.0)
    p.add_argument("--out", help="output CSV (default <SYMBOL>_<TF>.csv)")
    p.add_argument("--terminal-path", dest="path",
                   help="path to terminal64.exe if auto-detection fails")
    p.add_argument("--chunk-days", type=int, default=30, dest="chunk_days")
    a = p.parse_args()

    if not (mt5.initialize(path=a.path) if a.path else mt5.initialize()):
        sys.exit("could not connect to MT5: %s\n"
                 "Is the terminal running and logged in?" % (mt5.last_error(),))

    print("connected to %s" % (mt5.terminal_info().name,))

    if not mt5.symbol_select(a.symbol, True):
        avail = [s.name for s in (mt5.symbols_get() or []) if "XAU" in s.name.upper()]
        fail("symbol %r not available.  Gold symbols your broker offers: %s"
             % (a.symbol, ", ".join(avail) or "none found"))

    info = mt5.symbol_info(a.symbol)
    print("symbol %s | digits=%d | point=%g | contract size=%g"
          % (a.symbol, info.digits, info.point, info.trade_contract_size))

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=a.years * 365.25)
    print("fetching %s %s from %s to %s"
          % (a.symbol, a.timeframe, start.date(), end.date()))

    rows = fetch(a.symbol, TIMEFRAMES[a.timeframe], start, end, a.chunk_days)
    if not rows:
        fail("no bars returned — open the chart, press Home, scroll left to "
             "load history, then re-run")

    out = a.out or "%s_%s.csv" % (a.symbol, a.timeframe)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>",
                    "<CLOSE>", "<TICKVOL>", "<VOL>", "<SPREAD>"])
        fmt = "%%.%df" % info.digits
        for r in rows:
            t = datetime.fromtimestamp(int(r["time"]), tz=timezone.utc)
            w.writerow([t.strftime("%Y.%m.%d"), t.strftime("%H:%M"),
                        fmt % r["open"], fmt % r["high"], fmt % r["low"],
                        fmt % r["close"], int(r["tick_volume"]),
                        int(r["real_volume"]), int(r["spread"])])

    first = datetime.fromtimestamp(int(rows[0]["time"]), tz=timezone.utc)
    last = datetime.fromtimestamp(int(rows[-1]["time"]), tz=timezone.utc)
    print("\nwrote %d bars to %s\n  %s  ->  %s" % (len(rows), out, first, last))
    print("\nnow run:\n  python backtest_2candle.py %s --trades-csv trades.csv" % out)

    mt5.shutdown()


if __name__ == "__main__":
    main()
