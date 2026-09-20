# 24/7 Windows VPS setup

The Python MetaTrader5 package connects to a running MetaTrader 5 terminal. For a simple 24/7 setup, use a Windows VPS.

## Steps
1. Create a Windows VPS.
2. Install MetaTrader 5 on the VPS.
3. Log in to a DEMO trading account.
4. Clone this repository.
5. Open PowerShell in the project folder.
6. Run:
   ```powershell
   powershell -ExecutionPolicy Bypass -File deploy/windows-vps.ps1
   python run_scanner.py
   ```
7. Keep MT5 running.

The scanner is currently analysis/demo only and does not submit live orders.

## Security
Never commit an MT5 password, API token, or other secret to GitHub.
