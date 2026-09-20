import pandas as pd
import MetaTrader5 as mt5

TIMEFRAMES = {
    "M1": mt5.TIMEFRAME_M1, "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15, "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1, "H4": mt5.TIMEFRAME_H4,
}

def connect():
    if not mt5.initialize():
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")

def disconnect():
    mt5.shutdown()

def get_rates(symbol="XAUUSD", timeframe="M15", bars=2000):
    connect()
    try:
        if not mt5.symbol_select(symbol, True):
            raise RuntimeError(f"Cannot select {symbol}. Your broker may use another name such as XAUUSDm.")
        tf = TIMEFRAMES.get(timeframe.upper())
        if tf is None:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        rates = mt5.copy_rates_from_pos(symbol, tf, 0, int(bars))
        if rates is None or len(rates) == 0:
            raise RuntimeError(f"No rates returned: {mt5.last_error()}")
        df = pd.DataFrame(rates)
        df["timestamp"] = pd.to_datetime(df["time"], unit="s")
        return df[["timestamp","open","high","low","close","tick_volume"]].rename(columns={"tick_volume":"volume"})
    finally:
        disconnect()
