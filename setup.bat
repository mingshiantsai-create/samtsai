@echo off
REM 血壓監測應用 - Windows 啟動腳本

echo.
echo ====================================
echo  ❤️  血壓監測應用啟動工具
echo ====================================
echo.

REM 檢查 Python
echo [1/5] 檢查 Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Python 未安裝
    exit /b 1
)
echo ✓ Python 已安裝

REM 檢查 Node.js
echo [2/5] 檢查 Node.js...
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Node.js/npm 未安裝
    exit /b 1
)
echo ✓ Node.js/npm 已安裝

REM 設置後端
echo [3/5] 設置後端...
cd backend
if not exist "venv" (
    echo   建立虛擬環境...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo   安裝後端依賴...
pip install -q -r requirements.txt
cd ..
echo ✓ 後端已準備

REM 設置前端
echo [4/5] 設置前端...
cd frontend
if not exist "node_modules" (
    echo   安裝 npm 依賴...
    npm install -q
)
cd ..
echo ✓ 前端已準備

REM 啟動服務
echo [5/5] 啟動服務...
echo.
echo ✓ 啟動完成！
echo.
echo   後端：http://localhost:8000
echo   前端：http://localhost:5173
echo.
echo ====================================
echo 在 2 個新命令提示符中執行：
echo.
echo 終端 1 - 後端服務：
echo   cd backend ^&^& venv\Scripts\activate ^&^& python main.py
echo.
echo 終端 2 - 前端服務：
echo   cd frontend ^&^& npm run dev
echo.
echo 手機訪問：
echo   http://YOUR_IP:5173
echo ====================================
echo.
pause
