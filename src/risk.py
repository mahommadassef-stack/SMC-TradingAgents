def position_size(balance: float, risk_pct: float, entry: float, stop: float) -> float:
    distance = abs(entry - stop)
    if distance <= 0:
        return 0.0
    return (balance * risk_pct / 100.0) / distance
