@echo off
echo ========================================
echo   SISTEMA DE PORTARIA - INSTALACAO
echo ========================================
echo.
echo Instalando dependencias...
echo.

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ========================================
echo   INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Para executar o sistema, use:
echo   python sistema_portaria.py
echo.
pause
