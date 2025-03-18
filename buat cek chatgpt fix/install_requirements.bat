@echo off
echo Installing Python requirements...

REM Uninstall existing packages to avoid conflicts
pip uninstall -y Flask Flask-SQLAlchemy Flask-Login selenium PyMySQL Werkzeug webdriver-manager undetected-chromedriver

REM Install specific versions that are known to work together
pip install Flask==2.2.5 ^
            Flask-SQLAlchemy==3.0.2 ^
            Flask-Login==0.6.2 ^
            selenium==4.9.1 ^
            PyMySQL==1.0.2 ^
            Werkzeug==2.2.3 ^
            webdriver-manager==3.8.6 ^
            undetected-chromedriver==3.5.5

IF %ERRORLEVEL% NEQ 0 (
    echo Error installing requirements!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo Python requirements installed successfully!
echo.
pause 