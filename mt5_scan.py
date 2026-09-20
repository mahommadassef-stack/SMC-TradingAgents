import yaml
from src.mt5_data import get_rates
from src.strategy import generate_signals

with open("config.yaml", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

m = cfg["mt5"]
df = get_rates(m["symbol"], m["timeframe"], m["bars"])
signals = generate_signals(df, cfg["strategy"])
last = signals.iloc[-1]

side = {1: "BUY", -1: "SELL", 0: "NO TRADE"}[int(last["signal"])]
print("=== SMC MT5 Scanner ===")
print("Symbol:", m["symbol"])
print("Timeframe:", m["timeframe"])
print("Candle:", last["timestamp"])
print("Close:", last["close"])
print("Signal:", side)
print("Demo only:", m.get("demo_only", True))
