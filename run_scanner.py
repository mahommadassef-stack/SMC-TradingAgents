import time
import yaml
from src.mt5_data import get_rates
from src.strategy import generate_signals

def scan(cfg):
    m=cfg["mt5"]
    df=get_rates(m["symbol"],m["timeframe"],m["bars"])
    s=generate_signals(df,cfg["strategy"])
    row=s.iloc[-1]
    side={1:"BUY",-1:"SELL",0:"NO TRADE"}[int(row["signal"])]
    print(f'{row["timestamp"]} | {m["symbol"]} | {side} | close={row["close"]}', flush=True)

with open("config.yaml",encoding="utf-8") as f:
    cfg=yaml.safe_load(f)

print("SMC scanner running in DEMO mode", flush=True)
while True:
    try:
        scan(cfg)
    except Exception as e:
        print("scan error:",e,flush=True)
    time.sleep(60)
