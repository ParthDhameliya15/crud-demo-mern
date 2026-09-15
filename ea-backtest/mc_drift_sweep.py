#!/usr/bin/env python3
"""
Monte-Carlo drift sweep for the XAUUSD 2-candle breakout EA.

The EA has no time exit: a position runs until SL (the Candle-3 range, capped
at 30) or TP (250 away). That shape means its result is dominated by one
thing - how hard the market trends - not by the entry pattern. This script
quantifies that: it generates synthetic bar series at a controlled annual
drift, runs the real EA logic over them, and finds the drift at which the
strategy breaks even.

Bars are built from sub-steps of a random walk, so each bar's high and low come
from an actual traversed path rather than being drawn independently. That
matters: independently-drawn wicks make every entry land on a fake extreme and
inject a bias that is not the strategy's.

    python3 mc_drift_sweep.py --seeds 5 --years 2

This is a structural sensitivity test, not a profit forecast for gold.
"""

import argparse
import math
import random
import statistics
from argparse import Namespace

import backtest_2candle as bt

MINUTES_PER_YEAR = 365.0 * 24 * 60


def make_bars(n, drift_annual, vol_annual, s0, bar_minutes, seed, substeps=20):
    """Random walk sampled into OHLC bars with self-consistent highs/lows."""
    rng = random.Random(seed)
    dt = bar_minutes / MINUTES_PER_YEAR / substeps
    mu = drift_annual / 100.0
    sigma = vol_annual / 100.0
    sd = sigma * math.sqrt(dt)
    per = (mu - 0.5 * sigma * sigma) * dt

    import datetime
    t = datetime.datetime(2020, 1, 1)
    step = datetime.timedelta(minutes=bar_minutes)

    p = s0
    bars = []
    for _ in range(n):
        o = p
        hi = lo = p
        for _ in range(substeps):
            p *= math.exp(per + sd * rng.gauss(0, 1))
            hi = max(hi, p)
            lo = min(lo, p)
        bars.append(bt.Bar(t, round(o, 2), round(hi, 2), round(lo, 2), round(p, 2)))
        t += step
    return bars


def summarise(xs):
    """mean and standard error - with 50:1 reward:risk a bare mean is noise."""
    m = statistics.fmean(xs)
    se = (statistics.stdev(xs) / math.sqrt(len(xs))) if len(xs) > 1 else 0.0
    return m, se


def cfg_for(args, spread):
    return Namespace(
        tp=args.tp, max_c3=args.max_c3, lot=args.lot, offset=1, spread=spread,
        use_csv_spread=False, commission=0.0, point=0.01, digits=2,
        enable_buy=not args.no_buy, enable_sell=not args.no_sell,
        allow_multiple=True, ambiguous="sl",
    )


def evaluate(bars, cfg):
    """Net P&L including open positions marked to the final close.

    Marking open trades to market matters here: with a 250-wide TP many winners
    are still running when the data ends, and dropping them biases every result
    downward.
    """
    closed, still_open, _ = bt.run(bars, cfg)
    net = sum(t.pnl(cfg.lot) for t in closed)
    last = bars[-1].c
    for p in still_open:
        d = (last - p.entry) if p.side == "BUY" else (p.entry - last)
        net += d * cfg.lot * bt.CONTRACT_SIZE
    wins = sum(1 for t in closed if t.pnl(cfg.lot) > 0)
    return net, len(closed), wins, len(still_open)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--years", type=float, default=2.0)
    p.add_argument("--bar-minutes", type=int, default=15, dest="bar_minutes")
    p.add_argument("--vol", type=float, default=16.0, help="annualised vol %%")
    p.add_argument("--s0", type=float, default=2000.0)
    p.add_argument("--seeds", type=int, default=5)
    p.add_argument("--spread", type=float, default=25)
    p.add_argument("--tp", type=float, default=250.0)
    p.add_argument("--max-c3", type=float, default=30.0, dest="max_c3")
    p.add_argument("--lot", type=float, default=0.01)
    p.add_argument("--no-buy", action="store_true")
    p.add_argument("--no-sell", action="store_true")
    p.add_argument("--drifts", default="-20,-10,-5,0,5,10,15,20,30",
                   help="annual drift %% values to sweep")
    p.add_argument("--substeps", type=int, default=20,
                   help="random-walk sub-steps per bar; more = finer intrabar path")
    p.add_argument("--control", action="store_true",
                   help="only run the zero-drift zero-spread engine control")
    a = p.parse_args()

    n = int(a.years * MINUTES_PER_YEAR / a.bar_minutes)
    print("synthetic bars: %s x %dmin  (%.1f years)  vol %.0f%%  seeds %d"
          % (format(n, ","), a.bar_minutes, a.years, a.vol, a.seeds))

    if a.control:
        print("\nCONTROL: zero drift, zero spread -> a correct engine nets ~0\n")
        per = []
        for s in range(a.seeds):
            bars = make_bars(n, 0.0, a.vol, a.s0, a.bar_minutes, 1000 + s, a.substeps)
            net, ntr, w, op = evaluate(bars, cfg_for(a, 0))
            per.append(net / ntr if ntr else 0.0)
            print("  seed %d: %5d trades | %3d wins | %3d open | net $%+9.2f"
                  " | per trade $%+.3f" % (s, ntr, w, op, net, per[-1]))
        m, se = summarise(per)
        print("\n  mean per trade: $%+.3f  (SE %.3f, n=%d)" % (m, se, len(per)))
        print("  95%% CI: $%+.3f .. $%+.3f" % (m - 1.96 * se, m + 1.96 * se))
        print("  %s" % ("consistent with zero - no detectable engine bias"
                        if abs(m) < 1.96 * se else
                        "SIGNIFICANTLY different from zero - investigate"))
        return

    drifts = [float(x) for x in a.drifts.split(",")]
    print("\n  drift/yr |  trades |  wins | win% |   net $ (mean, 95% CI) | per trade")
    print("  ---------+---------+-------+------+-----------------------+----------")
    results = []
    for d in drifts:
        nets, trs, wins = [], [], []
        for s in range(a.seeds):
            bars = make_bars(n, d, a.vol, a.s0, a.bar_minutes, 2000 + s, a.substeps)
            net, ntr, w, _ = evaluate(bars, cfg_for(a, a.spread))
            nets.append(net); trs.append(ntr); wins.append(w)
        mn, se = summarise(nets)
        mt = sum(trs) / len(trs)
        mw = sum(wins) / len(wins)
        results.append((d, mn, se))
        star = "" if abs(mn) > 1.96 * se else "  (not sig.)"
        print("  %+7.1f%% | %7.0f | %5.1f | %4.1f | %+11.0f +/-%5.0f | %+7.3f%s"
              % (d, mt, mw, 100.0 * mw / mt if mt else 0, mn, 1.96 * se,
                 mn / mt if mt else 0, star))

    flat = min(results, key=lambda r: abs(r[0]))
    print("\n  Both sides are enabled, so this curve is V-shaped in drift, not")
    print("  monotonic: trend in EITHER direction feeds it, a flat market starves it.")
    print("  Judge it by |drift|, not by signed drift.")
    print("\n  flattest market tested (%+.1f%%/yr): net $%+.0f" % (flat[0], flat[1]))
    for sign, label in ((-1, "down-trending"), (1, "up-trending")):
        side = sorted((r for r in results if r[0] * sign > 0),
                      key=lambda r: abs(r[0]))
        good = [r for r in side if r[1] > 1.96 * r[2]]
        if good:
            print("  %-14s: clears noise from |drift| >= %.0f%%/yr"
                  % (label, abs(good[0][0])))
        else:
            print("  %-14s: never clears noise in the swept range" % label)


if __name__ == "__main__":
    main()
