import argparse, yaml, pandas as pd
from src.strategy import generate_signals
from src.backtest import run_backtest

p=argparse.ArgumentParser()
p.add_argument("--csv",required=True)
p.add_argument("--config",default="config.yaml")
a=p.parse_args()
with open(a.config,encoding="utf-8") as f: cfg=yaml.safe_load(f)
df=pd.read_csv(a.csv)
df["timestamp"]=pd.to_datetime(df["timestamp"])
summary,trades=run_backtest(generate_signals(df,cfg["strategy"]),cfg)
print("=== SMC TradingAgents Backtest ===")
for k,v in summary.items(): print(f"{k}: {v}")
