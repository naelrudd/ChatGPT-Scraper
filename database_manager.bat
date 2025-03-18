@echo off
cls
echo ====================================
echo Database Manager ChatGPT Scraper
echo ====================================

REM Check if MySQL is installed
echo Memeriksa instalasi MySQL...
where mysql >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] MySQL tidak ditemukan!
    echo.
    echo Silakan ikuti langkah berikut:
    echo 1. Download MySQL Community Server dari https://dev.mysql.com/downloads/mysql/
    echo 2. Install MySQL dan pastikan untuk:
    echo    - Centang "Add MySQL to System PATH" saat instalasi
    echo 3. Restart komputer Anda setelah instalasi
    echo 4. Jalankan script ini kembali
    echo.
    pause
    exit /b 1
)

echo MySQL terinstall dengan benar!
mysql --version
echo.

REM Set default credentials
set DB_USER=root
set DB_HOST=localhost
set DB_NAME=chatgpt_scraper

REM Try to load credentials from .env if exists
if exist .env (
    echo Membaca konfigurasi dari file .env...
    for /f "tokens=*" %%a in (.env) do (
        set %%a
    )
)

:MAIN_MENU
cls
echo ====================================
echo Database Manager ChatGPT Scraper
echo ====================================
echo Database: %DB_NAME%
echo Host: %DB_HOST%
echo User: %DB_USER%
echo ====================================
echo.
echo [1] Setup Database Baru
echo [2] Manajemen Database
echo [3] Konfigurasi Database
echo [4] Exit
echo.

set /p main_choice="Pilih menu (1-4): "

if "%main_choice%"=="1" goto SETUP_DATABASE
if "%main_choice%"=="2" goto MANAGE_DATABASE
if "%main_choice%"=="3" goto CONFIG_DATABASE
if "%main_choice%"=="4" exit

goto MAIN_MENU

:SETUP_DATABASE
cls
echo ====================================
echo Setup Database Baru
echo ====================================
echo.
echo Membuat database dan tabel...

mysql -u %DB_USER% -h %DB_HOST% -e "CREATE DATABASE IF NOT EXISTS %DB_NAME%;"
if %errorlevel% neq 0 (
    echo [ERROR] Gagal membuat database! Pastikan kredensial MySQL benar.
    pause
    goto MAIN_MENU
)

if exist database\schema.sql (
    mysql -u %DB_USER% -h %DB_HOST% %DB_NAME% < database\schema.sql
    if %errorlevel% equ 0 (
        echo.
        echo Database berhasil dibuat!
        echo - Database: %DB_NAME%
        echo - Tables: users, chat_histories, prompts, responses
    ) else (
        echo [ERROR] Gagal membuat tabel! Periksa file schema.sql
    )
) else (
    echo [ERROR] File schema.sql tidak ditemukan di folder database/
)

echo.
pause
goto MAIN_MENU

:MANAGE_DATABASE
cls
echo ====================================
echo Manajemen Database
echo ====================================
echo.
echo [1] Reset Database (Hapus semua data)
echo [2] Backup Database
echo [3] Restore Database
echo [4] Clear Data (Kosongkan tabel)
echo [5] Kembali ke Menu Utama
echo.

set /p manage_choice="Pilih menu (1-5): "

if "%manage_choice%"=="1" (
    echo.
    set /p confirm="Anda yakin ingin mereset database? (y/n): "
    if "%confirm%"=="y" (
        mysql -u %DB_USER% -h %DB_HOST% -e "DROP DATABASE IF EXISTS %DB_NAME%;"
        mysql -u %DB_USER% -h %DB_HOST% -e "CREATE DATABASE %DB_NAME%;"
        if exist database\schema.sql (
            mysql -u %DB_USER% -h %DB_HOST% %DB_NAME% < database\schema.sql
            echo Database telah direset!
        ) else (
            echo [ERROR] File schema.sql tidak ditemukan!
        )
    )
    pause
    goto MANAGE_DATABASE
)

if "%manage_choice%"=="2" (
    if not exist backup mkdir backup
    set timestamp=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
    set timestamp=%timestamp: =0%
    echo.
    echo Membuat backup database...
    mysqldump -u %DB_USER% -h %DB_HOST% %DB_NAME% > "backup\backup_%timestamp%.sql"
    if %errorlevel% equ 0 (
        echo Backup berhasil: backup\backup_%timestamp%.sql
    ) else (
        echo [ERROR] Gagal membuat backup!
    )
    pause
    goto MANAGE_DATABASE
)

if "%manage_choice%"=="3" (
    if not exist backup (
        echo [ERROR] Folder backup tidak ditemukan!
        pause
        goto MANAGE_DATABASE
    )
    echo.
    echo File backup yang tersedia:
    dir /b "backup\*.sql"
    echo.
    set /p backupfile="Masukkan nama file backup: "
    if exist "backup\%backupfile%" (
        echo Melakukan restore database dari %backupfile%...
        mysql -u %DB_USER% -h %DB_HOST% %DB_NAME% < "backup\%backupfile%"
        if %errorlevel% equ 0 (
            echo Database berhasil direstore!
        ) else (
            echo [ERROR] Gagal melakukan restore!
        )
    ) else (
        echo [ERROR] File backup tidak ditemukan!
    )
    pause
    goto MANAGE_DATABASE
)

if "%manage_choice%"=="4" (
    echo.
    set /p confirm="Anda yakin ingin mengosongkan semua tabel? (y/n): "
    if "%confirm%"=="y" (
        echo Mengosongkan tabel...
        mysql -u %DB_USER% -h %DB_HOST% %DB_NAME% -e "SET FOREIGN_KEY_CHECKS=0;"
        mysql -u %DB_USER% -h %DB_HOST% %DB_NAME% -e "TRUNCATE TABLE responses;"
        mysql -u %DB_USER% -h %DB_HOST% %DB_NAME% -e "TRUNCATE TABLE prompts;"
        mysql -u %DB_USER% -h %DB_HOST% %DB_NAME% -e "TRUNCATE TABLE chat_histories;"
        mysql -u %DB_USER% -h %DB_HOST% %DB_NAME% -e "TRUNCATE TABLE users;"
        mysql -u %DB_USER% -h %DB_HOST% %DB_NAME% -e "SET FOREIGN_KEY_CHECKS=1;"
        if %errorlevel% equ 0 (
            echo Semua tabel telah dikosongkan!
        ) else (
            echo [ERROR] Gagal mengosongkan tabel!
        )
    )
    pause
    goto MANAGE_DATABASE
)

if "%manage_choice%"=="5" goto MAIN_MENU
goto MANAGE_DATABASE

:CONFIG_DATABASE
cls
echo ====================================
echo Konfigurasi Database
echo ====================================
echo.
echo Konfigurasi saat ini:
echo - Database User: %DB_USER%
echo - Database Host: %DB_HOST%
echo - Database Name: %DB_NAME%
echo.
echo [1] Update Kredensial Database
echo [2] Test Koneksi Database
echo [3] Kembali ke Menu Utama
echo.

set /p config_choice="Pilih menu (1-3): "

if "%config_choice%"=="1" (
    echo.
    set /p new_user="Masukkan username MySQL [%DB_USER%]: "
    if not "%new_user%"=="" set DB_USER=%new_user%
    
    set /p new_host="Masukkan host MySQL [%DB_HOST%]: "
    if not "%new_host%"=="" set DB_HOST=%new_host%
    
    echo.
    echo Menyimpan konfigurasi ke file .env...
    echo DB_USER=%DB_USER%> .env
    echo DB_HOST=%DB_HOST%>> .env
    echo DB_NAME=%DB_NAME%>> .env
    echo Konfigurasi telah disimpan!
    pause
    goto CONFIG_DATABASE
)

if "%config_choice%"=="2" (
    echo.
    echo Testing koneksi database...
    mysql -u %DB_USER% -h %DB_HOST% -e "SELECT VERSION();" 2>nul
    if %errorlevel% equ 0 (
        echo Koneksi database berhasil!
    ) else (
        echo [ERROR] Gagal koneksi ke database! Periksa kredensial Anda.
    )
    pause
    goto CONFIG_DATABASE
)

if "%config_choice%"=="3" goto MAIN_MENU
goto CONFIG_DATABASE