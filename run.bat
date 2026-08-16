@echo off
echo Xabar TV - Yangiliklar saytini ishga tushirish
echo ============================================
echo.

echo 1. Python virtual muhit yaratish...
python -m venv venv

echo 2. Virtual muhitni faollashtirish...
call venv\Scripts\activate.bat

echo 3. Kerakli kutubxonalarni o'rnatish...
pip install -r requirements.txt

echo 4. Backend serverni ishga tushirish...
start cmd /k "call venv\Scripts\activate.bat && python api.py"

echo 5. 5 soniya kutish...
timeout /t 5

echo 6. Brauzerda saytni ochish...
start http://localhost:8000

echo.
echo Sayt ishga tushdi!
echo Backend: http://localhost:8000
echo Yangiliklarni qo'shish: POST /api/news
echo.
echo Ma'lumot uchun: 
echo - API hujjati: http://localhost:8000/docs
echo - Telegram kanal: @XabarTV_24
echo.
pause