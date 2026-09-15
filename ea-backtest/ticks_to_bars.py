#!/usr/bin/env python3
"""
Aggregate a tick export into OHLC bars for backtest_2candle.py.

Why this exists: the engine reads bars, and a coarse bar hides intrabar stop
touches. For this EA the stop sits 5-30 away while the target sits 250 away, so
coarse bars skip far more losses than wins - measured at +1.10, +0.68 and +0.35
per trade as intrabar resolution rose through 5, 20 and 80 sub-steps. Building
fine bars from real ticks pushes that bias down toward zero.

    python3 ticks_to_bars.py XAUUSD_ticks.csv --seconds 10 -o XAUUSD_S10.csv
    python3 backtest_2candle.py XAUUSD_S10.csv --use-csv-spread

Bars are built from the BID, matching how MT5 draws a chart, and each bar
carries the mean spread actually observed inside it - so --use-csv-spread
replays the real spread instead of a flat guess.

Note this changes what a "candle" means to the EA: the pattern is evaluated on
whatever bar size you build. To keep the EA's own signals intact, build bars at
its chart timeframe; use finer bars only to study how much the stop-touch bias
was costing you.

Input: DATE, TIME, BID, ASK[, LAST, VOLUME, FLAGS], tab or comma separated,
with TIME carrying seconds (and optionally milliseconds).
"""

import argparse
import csv
import sys
from datetime import datetime, timedelta


def parse_tick_time(date_s, time_s):
    s = "%s %s" % (date_s.replace("/", "."), time_s)
    for fmt in ("%Y.%m.%d %H:%M:%S.%f", "%Y.%m.%d %H:%M:%S",
                "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S",
                "%Y.%m.%d %H:%M", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError("unrecognised tick time: %r" % s)


def read_ticks(path):
    """Yield (time, bid, ask). Rows without a usable bid are skipped."""
    with open(path, newline="", encoding="utf-8-sig") as fh:
        sample = fh.read(8192)
        fh.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters="\t,;")
        except csv.Error:
            dialect = csv.excel_tab
        for row in csv.reader(fh, dialect):
            if not row or len(row) < 3:
                continue
            f = [x.strip().strip('"') for x in row]
            if f[0].lower().startswith(("<date", "date", "time")):
                continue
            try:
                t = parse_tick_time(f[0], f[1])
                bid = float(f[2])
                ask = float(f[3]) if len(f) > 3 and f[3] else bid
            except (ValueError, IndexError):
                continue
            if bid <= 0:
                continue
            if ask < bid:          # a stale or crossed quote is not usable
                ask = bid
            yield t, bid, ask


def floor_time(t, seconds):
    epoch = datetime(1970, 1, 1)
    n = int((t - epoch).total_seconds()) // seconds
    return epoch + timedelta(seconds=n * seconds)


def aggregate(ticks, seconds, point):
    """Group ticks into bars. Emits each bar once its slot is passed."""
    cur = None
    for t, bid, ask in ticks:
        slot = floor_time(t, seconds)
        if cur is None or slot != cur["t"]:
            if cur is not None:
                yield cur
            cur = {"t": slot, "o": bid, "h": bid, "l": bid, "c": bid,
                   "n": 0, "spread_sum": 0.0}
        cur["h"] = max(cur["h"], bid)
        cur["l"] = min(cur["l"], bid)
        cur["c"] = bid
        cur["n"] += 1
        cur["spread_sum"] += (ask - bid) / point
    if cur is not None:
        yield cur


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("ticks", help="tick CSV export")
    p.add_argument("--seconds", type=int, default=60,
                   help="bar size in seconds (default 60 = M1)")
    p.add_argument("-o", "--out", help="output bar CSV (default derived)")
    p.add_argument("--digits", type=int, default=2)
    p.add_argument("--point", type=float, default=0.01)
    a = p.parse_args()

    out = a.out or a.ticks.rsplit(".", 1)[0] + "_S%d.csv" % a.seconds
    fmt = "%%.%df" % a.digits

    n_bars = n_ticks = 0
    first = last = None
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["<DATE>", "<TIME>", "<OPEN>", "<HIGH>", "<LOW>",
                    "<CLOSE>", "<TICKVOL>", "<VOL>", "<SPREAD>"])
        for b in aggregate(read_ticks(a.ticks), a.seconds, a.point):
            spread = int(round(b["spread_sum"] / b["n"])) if b["n"] else 0
            w.writerow([b["t"].strftime("%Y.%m.%d"), b["t"].strftime("%H:%M:%S"),
                        fmt % b["o"], fmt % b["h"], fmt % b["l"], fmt % b["c"],
                        b["n"], 0, spread])
            n_bars += 1
            n_ticks += b["n"]
            first = first or b["t"]
            last = b["t"]

    if not n_bars:
        sys.exit("no bars produced - check the tick file's columns and format")
    print("%s ticks -> %s bars of %ds" % (format(n_ticks, ","),
                                          format(n_bars, ","), a.seconds))
    print("  %s  ->  %s" % (first, last))
    print("  written to %s" % out)
    print("\nnow run:\n  python3 backtest_2candle.py %s --use-csv-spread" % out)


if __name__ == "__main__":
    main()
