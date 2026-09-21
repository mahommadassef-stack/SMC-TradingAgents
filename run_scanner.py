import csv
import os
import time
import yaml
from src.mt5_data import get_rates
from src.strategy import generate_signals, trade_levels

LOG_FILE = "signals.csv"

def append_log(row, symbol, side, levels):
    new_file = not os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["timestamp","symbol","signal","close","long_score","short_score","session_ok","entry","stop_loss","take_profit","rr"])
        w.writerow([
            row["timestamp"], symbol, side, row["close"],
            int(row["long_score"]), int(row["short_score"]), bool(row["session_ok"]),
            levels["entry"] if levels else "",
            levels["stop"] if levels else "",
            levels["target"] if levels else "",
            levels["rr"] if levels else ""
        ])

def get_last_closed(cfg):
    m = cfg["mt5"]
    df = get_rates(m["symbol"], m["timeframe"], m["bars"])
    s = generate_signals(df, cfg["strategy"])
    # MT5's final row is the currently forming candle. Analyze the previous closed candle.
    return s.iloc[-2]

with open("config.yaml", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

symbol = cfg["mt5"]["symbol"]
last_processed = None
print("SMC scanner running in DEMO mode - closed M15 candles only", flush=True)

while True:
    try:
        row = get_last_closed(cfg)
        candle = str(row["timestamp"])
        if candle != last_processed:
            side = {1:"BUY", -1:"SELL", 0:"NO TRADE"}[int(row["signal"])]
            levels = trade_levels(row, cfg["strategy"])
            print(
                f'{candle} | {symbol} | {side} | close={row["close"]} | '
                f'L={int(row["long_score"])} S={int(row["short_score"])} '
                f'| session={bool(row["session_ok"])}',
                flush=True
            )
            if levels:
                print(
                    f'Entry={levels["entry"]} SL={levels["stop"]} '
                    f'TP={levels["target"]} R:R=1:{levels["rr"]}',
                    flush=True
                )
            append_log(row, symbol, side, levels)
            last_processed = candle
    except Exception as e:
        print("scan error:", e, flush=True)
    time.sleep(20)
