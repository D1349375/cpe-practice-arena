@echo off
chcp 65001 > nul
echo ============================================================
echo   正在啟動 CPE C 語言練習場 (GCC 14.2 環境)...
echo ============================================================
echo.
echo 練習環境路徑: %~dp0
echo.
start "" "http://localhost:5050"
python "%~dp0server.py"
pause
