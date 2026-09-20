$ErrorActionPreference = "Stop"
Write-Host "SMC TradingAgents - Windows VPS setup"
python -m pip install --upgrade pip
pip install -r requirements.txt
Write-Host "Dependencies installed."
Write-Host "Install MetaTrader 5 on this VPS, log in to a DEMO account, keep MT5 running, then run:"
Write-Host "python run_scanner.py"
