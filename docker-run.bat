@echo off
REM Docker 快速啟動腳本

echo.
echo ====================================
echo  ❤️  血壓監測應用 - Docker 部署
echo ====================================
echo.

REM 檢查 Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker 未安裝
    echo 請先安裝 Docker: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM 檢查 Docker Compose
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose 未安裝
    pause
    exit /b 1
)

echo ✓ Docker 和 Docker Compose 已安裝
echo.

REM 選擇操作
echo 選擇操作:
echo   1) 啟動應用 (docker-compose up -d)
echo   2) 停止應用 (docker-compose down)
echo   3) 查看日誌 (docker-compose logs -f)
echo   4) 重啟應用 (docker-compose restart)
echo   5) 清理所有 (docker-compose down -v)
echo.

set /p choice="請選擇 [1-5]: "

if "%choice%"=="1" (
    echo 啟動應用...
    docker-compose up -d
    timeout /t 5 /nobreak
    echo.
    echo ✓ 應用已啟動！
    echo.
    echo 訪問應用:
    echo   🌐 Web: http://localhost
    echo   📡 API: http://localhost:8000
    echo   📚 API 文檔: http://localhost:8000/docs
    echo.
    echo 查看日誌:
    echo   docker-compose logs -f
    echo.
    echo 停止應用:
    echo   docker-compose down
    echo.
) else if "%choice%"=="2" (
    echo 停止應用...
    docker-compose down
    echo ✓ 應用已停止
) else if "%choice%"=="3" (
    echo 顯示日誌 (Ctrl+C 退出)...
    docker-compose logs -f
) else if "%choice%"=="4" (
    echo 重啟應用...
    docker-compose restart
    echo ✓ 應用已重啟
) else if "%choice%"=="5" (
    set /p confirm="確定要清理所有容器和數據嗎? (y/n): "
    if /i "%confirm%"=="y" (
        echo 清理中...
        docker-compose down -v
        echo ✓ 已清理所有內容
    ) else (
        echo 已取消
    )
) else (
    echo ❌ 無效選擇
    exit /b 1
)

pause
