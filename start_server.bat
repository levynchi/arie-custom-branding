@echo off
echo.
echo 🚀 מפעיל שרת Django עם הגדרות נכונות...
echo.

:: Navigate to project directory
cd /d "%~dp0"

:: Check if virtual environment exists
if not exist "myenv" (
    echo ❌ סביבה וירטואלית לא נמצאה!
    echo יוצר סביבה וירטואלית חדשה...
    python -m venv myenv
)

:: Activate virtual environment
echo 📦 מפעיל סביבה וירטואלית...
call myenv\Scripts\activate

:: Check if activation worked
if "%VIRTUAL_ENV%"=="" (
    echo ❌ שגיאה בהפעלת הסביבה הוירטואלית!
    pause
    exit /b 1
)

echo ✅ סביבה וירטואלית פעילה: %VIRTUAL_ENV%

:: Install requirements if needed
if exist "requirements.txt" (
    echo 📋 מתקין dependencies...
    pip install -r requirements.txt
)

:: Start Django server
echo 🌐 מפעיל שרת Django...
echo 📍 השרת יפעל בכתובת: http://127.0.0.1:8000/
echo.
myenv\Scripts\python manage.py runserver

pause
