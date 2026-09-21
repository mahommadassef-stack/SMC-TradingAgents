import pandas as pd

def atr(df, period=14):
    prev=df["close"].shift(1)
    tr=pd.concat([df["high"]-df["low"],(df["high"]-prev).abs(),(df["low"]-prev).abs()],axis=1).max(axis=1)
    return tr.rolling(period).mean()

def generate_signals(df,cfg):
    df=df.copy().sort_values("timestamp").reset_index(drop=True)
    n=int(cfg.get("swing_lookback",5))
    df["atr"]=atr(df,int(cfg.get("atr_period",14)))
    df["prior_high"]=df["high"].rolling(n).max().shift(1)
    df["prior_low"]=df["low"].rolling(n).min().shift(1)
    df["bull_bos"]=df["close"]>df["prior_high"]
    df["bear_bos"]=df["close"]<df["prior_low"]
    df["bull_fvg"]=df["low"]>df["high"].shift(2)
    df["bear_fvg"]=df["high"]<df["low"].shift(2)

    # Liquidity sweep: wick through recent structure, close back inside.
    df["bull_sweep"]=(df["low"]<df["prior_low"]) & (df["close"]>df["prior_low"])
    df["bear_sweep"]=(df["high"]>df["prior_high"]) & (df["close"]<df["prior_high"])

    # CHoCH approximation: sweep followed by opposite structure break within recent bars.
    w=int(cfg.get("choch_window",4))
    df["bull_choch"]=df["bull_bos"] & (df["bull_sweep"].rolling(w).max().shift(1).fillna(0)>0)
    df["bear_choch"]=df["bear_bos"] & (df["bear_sweep"].rolling(w).max().shift(1).fillna(0)>0)

    # Simple order-block proxy: last opposite candle before displacement.
    df["bull_ob"]=df["bull_bos"] & (df["close"].shift(1)<df["open"].shift(1))
    df["bear_ob"]=df["bear_bos"] & (df["close"].shift(1)>df["open"].shift(1))

    # UTC session filter. London 07-11, New York 12-16.
    h=pd.to_datetime(df["timestamp"]).dt.hour
    df["session_ok"]=h.between(7,10) | h.between(12,15)

    score_long=df[["bull_bos","bull_fvg","bull_sweep","bull_choch","bull_ob"]].astype(int).sum(axis=1)
    score_short=df[["bear_bos","bear_fvg","bear_sweep","bear_choch","bear_ob"]].astype(int).sum(axis=1)
    minimum=int(cfg.get("minimum_confluence",2))
    df["long_score"]=score_long
    df["short_score"]=score_short
    df["signal"]=0
    df.loc[(score_long>=minimum)&df["session_ok"],"signal"]=1
    df.loc[(score_short>=minimum)&df["session_ok"],"signal"]=-1
    return df

def trade_levels(row,cfg):
    side=int(row["signal"])
    if side==0 or pd.isna(row["atr"]): return None
    entry=float(row["close"])
    dist=float(row["atr"])*float(cfg.get("atr_stop_multiplier",1.5))
    rr=float(cfg.get("reward_r_multiple",3.0))
    stop=entry-dist if side==1 else entry+dist
    target=entry+dist*rr if side==1 else entry-dist*rr
    return {"entry":round(entry,2),"stop":round(stop,2),"target":round(target,2),"rr":rr}
