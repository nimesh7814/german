@echo off
cd /d "%~dp0"
echo.
echo  ==========================================
echo    German A1 - Building HTML site
echo  ==========================================
echo.

echo [1/2] Syncing nav bars...
python nav_sync.py
if errorlevel 1 (
    echo ERROR in nav_sync.py
    pause
    exit /b 1
)

echo.
echo [2/2] Converting QMD to HTML...
python render_all.py
if errorlevel 1 (
    echo ERROR in render_all.py
    pause
    exit /b 1
)

echo.
echo  Done! Opening index.html ...
start index.html
pause
