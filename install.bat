@echo off
echo ========================================
echo Локальний Аналізатор Системних Журналів
echo Скрипт встановлення залежностей
echo ========================================
echo.

echo Перевірка Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не знайдено! 
    echo Будь ласка, встановіть Python 3.7+ з https://python.org
    pause
    exit /b 1
)

echo ✅ Python знайдено
python --version

echo.
echo Встановлення залежностей...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo ✅ Залежності встановлено успішно!
    echo.
    echo 🚀 Тепер ви можете запустити аналізатор:
    echo    python main.py
    echo.
    echo 📖 Або переглянути приклади:
    echo    python example.py
    echo.
) else (
    echo.
    echo ❌ Помилка встановлення залежностей
    echo Спробуйте встановити вручну:
    echo    pip install python-docx
    echo    pip install pywin32
    echo.
)

pause
