@echo off
echo Xabar TV - O'rnatish va ishga tushirish
echo ======================================
echo.

echo 1. Kerakli fayllarni tekshirish...
if not exist index.html echo ERROR: index.html topilmadi!
if not exist style.css echo ERROR: style.css topilmadi!
if not exist script.js echo ERROR: script.js topilmadi!
if not exist api.py echo ERROR: api.py topilmadi!
if not exist requirements.txt echo ERROR: requirements.txt topilmadi!

echo 2. Python o'rnatilganligini tekshirish...
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python o'rnatilmagan!
    echo Iltimos, Python 3.8+ o'rnating: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo 3. Virtual muhit yaratish...
if not exist venv (
    python -m venv venv
    echo Virtual muhit yaratildi
)

echo 4. Kutubxonalarni o'rnatish...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

echo 5. .env faylini tekshirish...
if not exist .env (
    echo TELEGRAM_BOT_TOKEN=your_token_here > .env
    echo .env fayl yaratildi. Iltimos, token ni o'rnating!
)

echo 6. Backend serverni ishga tushirish...
start cmd /k "call venv\Scripts\activate.bat && echo Backend server ishga tushmoqda... && python api.py"

echo 7. 5 soniya kutish...
timeout /t 5 /nobreak > nul

echo 8. Saytni ochish...
start http://localhost:8000

echo.
echo ============================================
echo Xabar TV muvaffaqiyatli ishga tushdi!
echo ============================================
echo.
echo Sayt: http://localhost:8000
echo API: http://localhost:8000/api/news
echo Swagger: http://localhost:8000/docs
echo.
echo Telegram kanal: @XabarTV_24
echo.
echo Yangilik qo'shish misol:
echo curl -X POST http://localhost:8000/api/news -H "Content-Type: application/json" -d "{\"title\":\"Test yangilik\",\"text\":\"Yangilik matni\",\"telegram_url\":\"https://t.me/XabarTV_24/1\"}"
echo.
pause