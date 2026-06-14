#!/bin/bash

# Docker 快速啟動腳本

echo "❤️ 血壓監測應用 - Docker 部署"
echo "================================"
echo ""

# 檢查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安裝"
    echo "請先安裝 Docker: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# 檢查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安裝"
    echo "請先安裝 Docker Compose"
    exit 1
fi

echo "✓ Docker 和 Docker Compose 已安裝"
echo ""

# 選擇操作
echo "選擇操作:"
echo "  1) 啟動應用 (docker-compose up -d)"
echo "  2) 停止應用 (docker-compose down)"
echo "  3) 查看日誌 (docker-compose logs -f)"
echo "  4) 重啟應用 (docker-compose restart)"
echo "  5) 清理所有 (docker-compose down -v)"
echo ""

read -p "請選擇 [1-5]: " choice

case $choice in
    1)
        echo "啟動應用..."
        docker-compose up -d
        sleep 5
        echo ""
        echo "✓ 應用已啟動！"
        echo ""
        echo "訪問應用:"
        echo "  🌐 Web: http://localhost"
        echo "  📡 API: http://localhost:8000"
        echo "  📚 API 文檔: http://localhost:8000/docs"
        echo ""
        echo "查看日誌:"
        echo "  docker-compose logs -f"
        echo ""
        echo "停止應用:"
        echo "  docker-compose down"
        ;;
    2)
        echo "停止應用..."
        docker-compose down
        echo "✓ 應用已停止"
        ;;
    3)
        echo "顯示日誌 (Ctrl+C 退出)..."
        docker-compose logs -f
        ;;
    4)
        echo "重啟應用..."
        docker-compose restart
        echo "✓ 應用已重啟"
        ;;
    5)
        read -p "確定要清理所有容器和數據嗎? (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            echo "清理中..."
            docker-compose down -v
            echo "✓ 已清理所有內容"
        else
            echo "已取消"
        fi
        ;;
    *)
        echo "❌ 無效選擇"
        exit 1
        ;;
esac
