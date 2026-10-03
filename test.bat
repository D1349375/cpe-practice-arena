@echo off
chcp 65001 > nul
echo ============================================================
echo   正在使用 GCC 編譯 solution.c ...
echo ============================================================
gcc -O2 -Wall "%~dp0solution.c" -o "%~dp0solution.exe" -lm

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [編譯失敗 Compilation Error] 請檢查語法錯誤！
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [編譯成功] 正在執行測試 (讀取 input.txt)...
echo ------------------------------------------------------------
"%~dp0solution.exe" < "%~dp0input.txt" > "%~dp0output.txt"
type "%~dp0output.txt"
echo ------------------------------------------------------------
echo.
if exist "%~dp0expected.txt" (
    echo [預期輸出 expected.txt]:
    echo ------------------------------------------------------------
    type "%~dp0expected.txt"
    echo ------------------------------------------------------------
)
echo.
echo 執行完畢！
pause
