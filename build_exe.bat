@echo off
echo ============================================
echo   Building CRF Auto-Bookmarker .exe
echo ============================================
echo.

pyinstaller --noconsole --onefile --name "CRF_AutoBookmarker" --add-data "bookmarker.py;." app.py

echo.
echo ============================================
echo   Build complete!
echo   Find your .exe in: dist\CRF_AutoBookmarker.exe
echo ============================================
pause