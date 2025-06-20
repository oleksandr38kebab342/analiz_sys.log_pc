@echo off
echo ========================================
echo Локальний Аналізатор Системних Журналів
echo ========================================
echo.

:menu
echo Виберіть дію:
echo 1 - Запустити аналіз системних журналів
echo 2 - Запустити демонстрацію з тестовими даними
echo 3 - Перевірити готовність системи
echo 4 - Переглянути приклади використання
echo 5 - Встановити залежності
echo 0 - Вихід
echo.
set /p choice="Ваш вибір (0-5): "

if "%choice%"=="1" goto analysis
if "%choice%"=="2" goto demo
if "%choice%"=="3" goto test
if "%choice%"=="4" goto examples
if "%choice%"=="5" goto install
if "%choice%"=="0" goto exit
goto menu

:analysis
echo.
echo 🔍 Запуск аналізу системних журналів...
echo.
python main.py
echo.
pause
goto menu

:demo
echo.
echo 🎭 Запуск демонстрації...
echo.
python demo.py
echo.
pause
goto menu

:test
echo.
echo 🧪 Перевірка готовності системи...
echo.
python test_system.py
echo.
pause
goto menu

:examples
echo.
echo 📖 Приклади використання...
echo.
python example.py
echo.
pause
goto menu

:install
echo.
echo 📦 Встановлення залежностей...
echo.
call install.bat
echo.
pause
goto menu

:exit
echo.
echo До побачення!
echo.
