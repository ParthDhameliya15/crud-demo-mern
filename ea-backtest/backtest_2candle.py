#!/usr/bin/env python3
"""
Bar-by-bar backtester for XAUUSD_2Candle_BuySellEA.mq5 (v1.40).

Replicates the EA's logic exactly:

  BUY  : Red -> Green -> Green, C3.close >= C2.high,
         enter on C4 break of C3.high + offset.  SL = C3.low, TP = trigger + TP_dist
  SELL : Green -> Red -> Red,   C3.close <= C2.low,
         enter on C4 break of C3.low - offset.   SL = C3.high, TP = trigger - TP_dist

  - Candle-3 size filter (High-Low <= InpMaxC3Size)
  - setup arms on a new bar, expires when that bar closes without a break
  - one setup = one entry
  - positions have NO time-based exit: they run until SL or TP

Bid/ask modelling matches the EA: BUY breaks/exits on ask/bid respectively,
SELL the mirror. Requires no third-party packages.

Usage:
    python3 backtest_2candle.py data.csv --tp 250 --max-c3 30 --lot 0.01 --spread 25

Input: MT5 "Save as CSV" bar export, tab- or comma-separated, with or without
a <DATE> header row:
    <DATE> <TIME> <OPEN> <HIGH> <LOW> <CLOSE> <TICKVOL> <VOL> <SPREAD>
"""

import argparse
import csv
import sys
from datetime import datetime

CONTRACT_SIZE = 100.0  # XAUUSD: 100 oz per 1.00 lot -> 1.00 price move = $100/lot


# ----------------------------------------------------------------- data ----
class Bar:
    __slots__ = ("t", "o", "h", "l", "c", "spread")

    def __init__(self, t, o, h, l, c, spread=None):
        self.t, self.o, self.h, self.l, self.c, self.spread = t, o, h, l, c, spread

    @property
    def green(self):
        return self.c > self.o

    @property
    def red(self):
        return self.c < self.o


def _parse_time(*parts):
    s = " ".join(p for p in parts if p).replace("/", ".").strip()
    for fmt in ("%Y.%m.%d %H:%M:%S", "%Y.%m.%d %H:%M", "%Y.%m.%d",
                "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError("unrecognised datetime: %r" % s)


def load_bars(path):
    """Read an MT5 bar export. Tolerates tab/comma/semicolon and header rows."""
    with open(path, newline="", encoding="utf-8-sig") as fh:
        sample = fh.read(4096)
        fh.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters="\t,;")
        except csv.Error:
            dialect = csv.excel_tab
        rows = [r for r in csv.reader(fh, dialect) if r and any(f.strip() for f in r)]

    bars = []
    for row in rows:
        f = [x.strip().strip('"') for x in row]
        if not f or f[0].lower().startswith(("<date", "date", "time")):
            continue  # header
        try:
            # date+time in separate columns, or one combined column
            if len(f) >= 6 and ":" in f[1]:
                t = _parse_time(f[0], f[1])
                nums = f[2:]
            else:
                t = _parse_time(f[0])
                nums = f[1:]
            o, h, l, c = (float(nums[i]) for i in range(4))
            spread = float(nums[6]) if len(nums) > 6 and nums[6] else None
        except (ValueError, IndexError):
            continue  # skip malformed line rather than abort the run
        bars.append(Bar(t, o, h, l, c, spread))

    bars.sort(key=lambda b: b.t)
    return bars


# ------------------------------------------------------------ positions ----
class Position:
    __slots__ = ("side", "t_open", "entry", "sl", "tp", "t_close", "exit", "reason")

    def __init__(self, side, t_open, entry, sl, tp):
        self.side, self.t_open, self.entry, self.sl, self.tp = side, t_open, entry, sl, tp
        self.t_close = self.exit = self.reason = None

    def pnl(self, lot):
        d = (self.exit - self.entry) if self.side == "BUY" else (self.entry - self.exit)
        return d * lot * CONTRACT_SIZE


# ------------------------------------------------------------- backtest ----
def run(bars, cfg):
    point = cfg.point
    spread_px = cfg.spread * point
    offset = cfg.offset * point

    open_pos, closed = [], []
    skipped_single = 0

    def spread_at(bar):
        if cfg.use_csv_spread and bar.spread is not None:
            return bar.spread * point
        return spread_px

    def resolve(pos, bar, sp):
        """Return (exit_price, reason) if this bar closes the position."""
        if pos.side == "BUY":                       # exits checked on bid
            hit_sl, hit_tp = bar.l <= pos.sl, bar.h >= pos.tp
        else:                                        # exits checked on ask
            hit_sl, hit_tp = bar.h + sp >= pos.sl, bar.l + sp <= pos.tp
        if hit_sl and hit_tp:
            return (pos.sl, "SL") if cfg.ambiguous == "sl" else (pos.tp, "TP")
        if hit_sl:
            return pos.sl, "SL"
        if hit_tp:
            return pos.tp, "TP"
        return None, None

    for i in range(3, len(bars)):
        cur = bars[i]          # Candle-4  (the bar we may enter on)
        c3, c2, c1 = bars[i - 1], bars[i - 2], bars[i - 3]
        sp = spread_at(cur)

        # --- close any open positions that this bar takes out -------------
        for pos in list(open_pos):
            price, why = resolve(pos, cur, sp)
            if why:
                pos.exit, pos.reason, pos.t_close = price, why, cur.t
                open_pos.remove(pos)
                closed.append(pos)

        # --- arm setups from the three just-closed candles ----------------
        c3_size = c3.h - c3.l
        size_ok = c3_size <= cfg.max_c3

        buy_setup = (cfg.enable_buy and c1.red and c2.green and c3.green
                     and c3.c >= c2.h and size_ok)
        sell_setup = (cfg.enable_sell and c1.green and c2.red and c3.red
                      and c3.c <= c2.l and size_ok)

        for side in ("BUY", "SELL"):
            if side == "BUY" and not buy_setup:
                continue
            if side == "SELL" and not sell_setup:
                continue

            if side == "BUY":
                trig = round(c3.h + offset, cfg.digits)
                # EA compares ASK >= trigger; ask = bid + spread
                if cur.h + sp < trig:
                    continue
                entry = max(trig, cur.o + sp)          # gap-open fills at open
                sl, tp = round(c3.l, cfg.digits), round(trig + cfg.tp, cfg.digits)
            else:
                trig = round(c3.l - offset, cfg.digits)
                if cur.l > trig:                        # EA compares BID <= trigger
                    continue
                entry = min(trig, cur.o)
                sl, tp = round(c3.h, cfg.digits), round(trig - cfg.tp, cfg.digits)

            if not cfg.allow_multiple and open_pos:
                skipped_single += 1
                continue

            pos = Position(side, cur.t, entry, sl, tp)

            # same-bar SL/TP after entry (conservative: this bar can still close it)
            price, why = resolve(pos, cur, sp)
            if why:
                pos.exit, pos.reason, pos.t_close = price, why, cur.t
                closed.append(pos)
            else:
                open_pos.append(pos)

    return closed, open_pos, skipped_single


# ---------------------------------------------------------------- stats ----
def report(closed, still_open, skipped, bars, cfg):
    lot = cfg.lot
    comm = cfg.commission * lot * 2  # round turn

    def block(name, trades):
        if not trades:
            return "%s: no trades\n" % name
        pnls = [t.pnl(lot) - comm for t in trades]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p <= 0]
        gp, gl = sum(wins), -sum(losses)
        net = sum(pnls)

        eq, peak, mdd = 0.0, 0.0, 0.0
        for p in pnls:
            eq += p
            peak = max(peak, eq)
            mdd = max(mdd, peak - eq)

        holds = [(t.t_close - t.t_open).total_seconds() / 86400.0 for t in trades]
        out = [
            "%s" % name,
            "  trades            : %d" % len(trades),
            "  wins / losses     : %d / %d" % (len(wins), len(losses)),
            "  win rate          : %.1f%%" % (100.0 * len(wins) / len(trades)),
            "  gross profit      : %.2f" % gp,
            "  gross loss        : %.2f" % gl,
            "  NET PROFIT        : %.2f" % net,
            "  profit factor     : %s" % ("inf" if gl == 0 else "%.2f" % (gp / gl)),
            "  expectancy/trade  : %.2f" % (net / len(trades)),
            "  avg win / avg loss: %.2f / %.2f" % (
                (gp / len(wins)) if wins else 0.0,
                (gl / len(losses)) if losses else 0.0),
            "  largest win/loss  : %.2f / %.2f" % (max(pnls), min(pnls)),
            "  max closed-eq DD  : %.2f" % mdd,
            "  avg hold          : %.1f days   (max %.1f)" % (
                sum(holds) / len(holds), max(holds)),
            "",
        ]
        return "\n".join(out)

    lines = [
        "=" * 62,
        "  XAUUSD 2-Candle Breakout EA  -  backtest",
        "=" * 62,
        "bars              : %d   (%s -> %s)" % (
            len(bars), bars[0].t, bars[-1].t) if bars else "no bars",
        "lot %.2f | TP %.2f | maxC3 %.2f | offset %dpt | spread %s | comm %.2f/lot/side"
        % (cfg.lot, cfg.tp, cfg.max_c3, cfg.offset,
           "per-bar from CSV" if cfg.use_csv_spread else "%dpt" % cfg.spread,
           cfg.commission),
        "both-sides-open   : %s | ambiguous bar resolves to: %s"
        % (cfg.allow_multiple, cfg.ambiguous.upper()),
        "",
        block("ALL TRADES", closed),
        block("BUY ONLY", [t for t in closed if t.side == "BUY"]),
        block("SELL ONLY", [t for t in closed if t.side == "SELL"]),
    ]
    if skipped:
        lines.append("entries skipped (single-position mode): %d" % skipped)
    if still_open:
        lines.append("STILL OPEN at end of data: %d  (excluded from stats)" % len(still_open))
        for p in still_open[:10]:
            lines.append("   %s %s entry %.2f  SL %.2f  TP %.2f"
                         % (p.t_open, p.side, p.entry, p.sl, p.tp))
    return "\n".join(lines)


def write_trades_csv(path, closed, lot, comm):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["side", "open_time", "entry", "sl", "tp",
                    "close_time", "exit", "reason", "pnl_usd"])
        for t in closed:
            w.writerow([t.side, t.t_open, "%.2f" % t.entry, "%.2f" % t.sl,
                        "%.2f" % t.tp, t.t_close, "%.2f" % t.exit, t.reason,
                        "%.2f" % (t.pnl(lot) - comm)])


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("csv", help="MT5 bar export for XAUUSD")
    p.add_argument("--tp", type=float, default=250.0, help="TP distance in price")
    p.add_argument("--max-c3", type=float, default=30.0, dest="max_c3")
    p.add_argument("--lot", type=float, default=0.01)
    p.add_argument("--offset", type=int, default=1, help="break offset, points")
    p.add_argument("--spread", type=float, default=25, help="spread in points")
    p.add_argument("--use-csv-spread", action="store_true", dest="use_csv_spread",
                   help="use the per-bar spread column when present")
    p.add_argument("--commission", type=float, default=0.0, help="USD per lot per side")
    p.add_argument("--point", type=float, default=0.01)
    p.add_argument("--digits", type=int, default=2)
    p.add_argument("--no-buy", action="store_false", dest="enable_buy")
    p.add_argument("--no-sell", action="store_false", dest="enable_sell")
    p.add_argument("--single-position", action="store_false", dest="allow_multiple")
    p.add_argument("--ambiguous", choices=("sl", "tp"), default="sl",
                   help="when one bar spans both SL and TP (default: sl = pessimistic)")
    p.add_argument("--trades-csv", help="write the full trade list here")
    cfg = p.parse_args(argv)

    bars = load_bars(cfg.csv)
    if len(bars) < 5:
        sys.exit("error: need at least 5 bars, got %d - check the CSV format" % len(bars))

    closed, still_open, skipped = run(bars, cfg)
    print(report(closed, still_open, skipped, bars, cfg))
    if cfg.trades_csv:
        write_trades_csv(cfg.trades_csv, closed, cfg.lot, cfg.commission * cfg.lot * 2)
        print("\ntrade list written to %s" % cfg.trades_csv)


if __name__ == "__main__":
    main()
