import pandas as pd

def atr(df, period=14):
    prev = df["close"].shift(1)
    tr = pd.concat([(df["high"]-df["low"]), (df["high"]-prev).abs(), (df["low"]-prev).abs()], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def generate_signals(df, cfg):
    df = df.copy().sort_values("timestamp").reset_index(drop=True)
    n = int(cfg.get("swing_lookback", 5))
    df["atr"] = atr(df, int(cfg.get("atr_period", 14)))
    df["prior_high"] = df["high"].rolling(n).max().shift(1)
    df["prior_low"] = df["low"].rolling(n).min().shift(1)
    df["bull_bos"] = df["close"] > df["prior_high"]
    df["bear_bos"] = df["close"] < df["prior_low"]
    df["bull_fvg"] = df["low"] > df["high"].shift(2)
    df["bear_fvg"] = df["high"] < df["low"].shift(2)
    use_fvg = bool(cfg.get("use_fvg_filter", True))
    df["signal"] = 0
    df.loc[df["bull_bos"] & (df["bull_fvg"] if use_fvg else True), "signal"] = 1
    df.loc[df["bear_bos"] & (df["bear_fvg"] if use_fvg else True), "signal"] = -1
    return df
