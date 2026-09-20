from collections import defaultdict
from .risk import position_size

def run_backtest(df, config):
    start = float(config["account"]["starting_balance"])
    balance = start
    risk = config["risk"]; strat = config["strategy"]
    daily_pnl, daily_count, trades = defaultdict(float), defaultdict(int), []
    for i, row in df.iterrows():
        if not row["signal"] or row["atr"] != row["atr"]: continue
        day = row["timestamp"].date()
        if daily_count[day] >= int(risk["max_trades_per_day"]): continue
        if daily_pnl[day] <= -(balance * float(risk["max_daily_loss_pct"]) / 100): continue
        side, entry = int(row["signal"]), float(row["close"])
        dist = float(row["atr"]) * float(strat["atr_stop_multiplier"])
        stop = entry - dist if side == 1 else entry + dist
        target = entry + dist*float(strat["reward_r_multiple"]) if side == 1 else entry - dist*float(strat["reward_r_multiple"])
        qty = position_size(balance, float(risk["risk_per_trade_pct"]), entry, stop)
        # Look forward until target or stop is hit.
        outcome = None
        for _, future in df.iloc[i+1:].iterrows():
            if side == 1:
                if future["low"] <= stop: outcome = -1; break
                if future["high"] >= target: outcome = float(strat["reward_r_multiple"]); break
            else:
                if future["high"] >= stop: outcome = -1; break
                if future["low"] <= target: outcome = float(strat["reward_r_multiple"]); break
        if outcome is None: continue
        pnl = balance * float(risk["risk_per_trade_pct"])/100 * outcome
        balance += pnl; daily_pnl[day] += pnl; daily_count[day] += 1
        trades.append({"time":str(row["timestamp"]),"side":side,"entry":entry,"stop":stop,"target":target,"qty":qty,"pnl":round(pnl,2)})
    wins=sum(t["pnl"]>0 for t in trades)
    return {"start":start,"end":round(balance,2),"net":round(balance-start,2),"trades":len(trades),"win_rate":round(100*wins/len(trades),2) if trades else 0}, trades
