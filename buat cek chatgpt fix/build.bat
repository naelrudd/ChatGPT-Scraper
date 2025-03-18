@echo off
echo ====================================
echo Building ChatGPT Scraper Executable
echo ====================================

REM Install requirements jika belum
pip install -r requirements.txt

REM Build executable
pyinstaller --noconfirm --onefile --windowed --icon=icon.ico --add-data "templates;templates" --add-data "static;static" --name "ChatGPT-Scraper" app.py

echo ====================================
echo Build completed!
echo Executable location: dist/ChatGPT-Scraper.exe
echo ====================================
pause 