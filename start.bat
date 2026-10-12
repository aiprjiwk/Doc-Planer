@echo off
title IWK Document Plan Dashboard
echo ========================================================
echo   Launching IWK Document Plan Dashboard...
echo   Excel Formula-driven Tracking & Auto-Maintenance App
echo ========================================================
cd /d "%~dp0"

echo Opening browser at http://localhost:8502 ...
start "" "http://localhost:8502"

python -m streamlit run app.py --server.port 8502 --server.address localhost --server.headless false

pause
