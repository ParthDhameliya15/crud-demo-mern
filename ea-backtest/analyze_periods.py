#!/usr/bin/env python3
"""
Period-by-period report for the XAUUSD 2-candle breakout EA.

One net-profit figure over 13 years hides the thing that actually drives this
strategy. The EA has no time exit, so its result tracks how hard the market
trended, and a Monte-Carlo sweep of the same logic (mc_drift_sweep.py) came out
V-shaped in drift: trend in either direction feeds it, a flat market starves it,
and below roughly 10%/yr of drift the result never clears noise.

So this splits the data into periods, and for each one reports the realised
drift alongside the P&L - which puts every period on that curve.

    python3 analyze_periods.py XAUUSD_M15.csv --by year

Each period is backtested independently; positions do not carry across a
boundary. Positions still open at a period's end are marked to its final close
rather than dropped, because with a 250-wide TP the open set is where the
winners are and dropping it biases every period downward.

Every P&L is a RANGE, not a number: one bar can span both the stop and the
target, and OHLC data cannot say which came first. The low end assumes the stop
hit first, the high end the target. If the two ends disagree about the sign,
the data cannot answer the question - say so rather than picking a side.
"""

import argparse
import math
from argparse import Namespace
from collections import OrderedDict

import backtest_2candle as bt


def key_for(bar, by):
    if by == "year":
        return "%d" % bar.t.year
    if by == "quarter":
        return "%d-Q%d" % (bar.t.year, (bar.t.month - 1) // 3 + 1)
    if by == "month":
        return "%d-%02d" % (bar.t.year, bar.t.month)
    return "all"


def split(bars, by, ranges):
    groups = OrderedDict()
    if ranges:
        import datetime
        for spec in ranges:
            lo, hi = spec.split(":")
            lo = datetime.datetime.strptime(lo, "%Y-%m-%d")
            hi = datetime.datetime.strptime(hi, "%Y-%m-%d")
            groups[spec] = [b for b in bars if lo <= b.t <= hi]
    else:
        for b in bars:
            groups.setdefault(key_for(b, by), []).append(b)
    return groups


MIN_YEARS_TO_ANNUALISE = 0.5


def realised_drift(bars):
    """Change in close over the period, as (value_pct, annualised?).

    Annualising a short span explodes - a 5% move over four hours annualises to
    an astronomical number - so spans under half a year report the raw total
    change instead, flagged by the caller.
    """
    yrs = (bars[-1].t - bars[0].t).total_seconds() / (365.25 * 86400)
    if yrs <= 0 or bars[0].c <= 0:
        return 0.0, True
    total = (bars[-1].c / bars[0].c - 1.0) * 100.0
    if yrs < MIN_YEARS_TO_ANNUALISE:
        return total, False
    try:
        return ((bars[-1].c / bars[0].c) ** (1.0 / yrs) - 1.0) * 100.0, True
    except OverflowError:
        return total, False


def evaluate(bars, cfg):
    closed, still_open, _ = bt.run(bars, cfg)
    comm = cfg.commission * cfg.lot * 2
    pnls = [t.pnl(cfg.lot) - comm for t in closed]
    last = bars[-1].c
    for p in still_open:
        d = (last - p.entry) if p.side == "BUY" else (p.entry - last)
        pnls.append(d * cfg.lot * bt.CONTRACT_SIZE - comm)

    net = sum(pnls)
    wins = [x for x in pnls if x > 0]
    gl = -sum(x for x in pnls if x <= 0)
    eq = peak = mdd = 0.0
    for x in pnls:
        eq += x
        peak = max(peak, eq)
        mdd = max(mdd, peak - eq)
    return {
        "n": len(pnls), "wins": len(wins), "net": net, "mdd": mdd,
        "pf": (sum(wins) / gl) if gl > 0 else float("inf"),
        "open": len(still_open),
    }


def cfg_for(a, ambiguous):
    return Namespace(
        tp=a.tp, max_c3=a.max_c3, lot=a.lot, offset=a.offset, spread=a.spread,
        use_csv_spread=a.use_csv_spread, commission=a.commission, point=0.01,
        digits=2, enable_buy=not a.no_buy, enable_sell=not a.no_sell,
        allow_multiple=not a.single_position, ambiguous=ambiguous,
    )


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("csv")
    p.add_argument("--by", default="year", choices=("year", "quarter", "month", "all"))
    p.add_argument("--range", action="append", dest="ranges",
                   help="custom period YYYY-MM-DD:YYYY-MM-DD (repeatable)")
    p.add_argument("--tp", type=float, default=250.0)
    p.add_argument("--max-c3", type=float, default=30.0, dest="max_c3")
    p.add_argument("--lot", type=float, default=0.01)
    p.add_argument("--offset", type=int, default=1)
    p.add_argument("--spread", type=float, default=25)
    p.add_argument("--use-csv-spread", action="store_true", dest="use_csv_spread")
    p.add_argument("--commission", type=float, default=0.0)
    p.add_argument("--no-buy", action="store_true")
    p.add_argument("--no-sell", action="store_true")
    p.add_argument("--single-position", action="store_true")
    p.add_argument("--min-bars", type=int, default=500, dest="min_bars")
    a = p.parse_args()

    bars = bt.load_bars(a.csv)
    if len(bars) < 5:
        raise SystemExit("need at least 5 bars, got %d" % len(bars))

    groups = split(bars, a.by, a.ranges)
    print("=" * 96)
    print("  XAUUSD 2-candle EA - period report   (%s bars, %s -> %s)"
          % (format(len(bars), ","), bars[0].t.date(), bars[-1].t.date()))
    print("  P&L shown as a RANGE: [stop-first .. target-first]. "
          "OHLC cannot resolve same-bar ties.")
    print("=" * 96)
    print("  %-12s %7s %10s %7s %6s %22s %9s %9s"
          % ("period", "bars", "drift/yr", "trades", "win%", "net $ range",
             "PF(pess)", "maxDD"))
    # "*" marks a span too short to annualise - raw total change shown instead
    print("  " + "-" * 92)

    tot_lo = tot_hi = 0.0
    for name, gb in groups.items():
        if len(gb) < a.min_bars:
            print("  %-12s %7s   (skipped - under %d bars)"
                  % (name, format(len(gb), ","), a.min_bars))
            continue
        lo = evaluate(gb, cfg_for(a, "sl"))
        hi = evaluate(gb, cfg_for(a, "tp"))
        tot_lo += lo["net"]; tot_hi += hi["net"]
        d, annualised = realised_drift(gb)
        if not annualised:
            flag = "  <- partial period, total change not annualised"
        elif abs(d) < 10:
            flag = "  <- flat, expect noise"
        else:
            flag = ""
        print("  %-12s %7s %+8.1f%%%s %7d %5.1f%% %10.0f .. %-10.0f %8.2f %9.0f%s"
              % (name, format(len(gb), ","), d, " " if annualised else "*", lo["n"],
                 100.0 * lo["wins"] / lo["n"] if lo["n"] else 0,
                 lo["net"], hi["net"], lo["pf"], lo["mdd"], flag))

    print("  " + "-" * 92)
    print("  %-12s %52s %10.0f .. %.0f" % ("TOTAL", "", tot_lo, tot_hi))
    if (tot_lo < 0) != (tot_hi < 0):
        print("\n  The two ends disagree on the sign. On this data the strategy's")
        print("  profitability is decided by same-bar tie-breaks, which OHLC bars")
        print("  cannot resolve. Re-run in MT5 with real ticks before concluding.")
    print("\n  Periods flagged flat (|drift| < 10%/yr) are where the Monte-Carlo")
    print("  study found results indistinguishable from noise. Weight them lightly.")


if __name__ == "__main__":
    main()
